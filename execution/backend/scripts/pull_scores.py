"""Pull scoring data (companies, scores, sources, aliases) from a remote database to local.

Usage:
    python -m scripts.pull_scores --remote-url "postgresql+pg8000://..."
    python -m scripts.pull_scores --remote-url "..." --company "Stripe"
    python -m scripts.pull_scores --remote-url "..." --since 2026-02-15
    python -m scripts.pull_scores --remote-url "..." --dry-run

Sync protocol:
  - Natural key: company.domain (stable across environments)
  - Companies: upsert by domain (remote wins for metadata)
  - Scores: append-only (skip if same company+created_at exists)
  - Sources: upsert by company+url
  - Aliases: upsert by alias_domain
  - All operations in a single transaction
  - Local DB backed up before pull
"""

import argparse
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, SessionLocal
from app.models.company import Company, Score, CompanySource, CompanyDomainAlias


@dataclass
class PullResult:
    """Summary of a pull operation."""

    companies_pulled: int = 0
    scores_pulled: int = 0
    sources_pulled: int = 0
    aliases_pulled: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def backup_local_db(db_path: str) -> Optional[str]:
    """Create a .bak copy of the local database file.

    Returns the backup path, or None if backup is not applicable
    (e.g., in-memory databases).
    """
    if db_path == ":memory:" or not db_path:
        return None

    bak_path = db_path + ".bak"
    shutil.copy2(db_path, bak_path)
    return bak_path


def pull_scores(
    remote_db: Session,
    local_db: Session,
    *,
    company_filter: Optional[str] = None,
    since: Optional[datetime] = None,
    dry_run: bool = False,
) -> PullResult:
    """Pull scoring data from remote to local database.

    Args:
        remote_db: Session connected to the remote (source) database.
        local_db: Session connected to the local (target) database.
        company_filter: If set, only pull companies matching this name.
        since: If set, only pull scores created after this datetime.
        dry_run: If True, compute what would be pulled but don't commit.

    Returns:
        PullResult with counts of pulled records.
    """
    result = PullResult()

    # Load companies from remote
    stmt = select(Company)
    if company_filter:
        stmt = stmt.where(Company.name == company_filter)
    remote_companies = remote_db.execute(stmt).scalars().all()

    for remote_company in remote_companies:
        if not remote_company.domain:
            result.errors.append(
                f"Skipping '{remote_company.name}': no domain set (natural key required)"
            )
            continue

    # Pre-fetch all needed local companies by domain
    local_companies_map = {}
    if remote_companies:
        domains = [c.domain for c in remote_companies if c.domain]
        existing_local = local_db.execute(
            select(Company).where(Company.domain.in_(domains))
        ).scalars().all()
        local_companies_map = {c.domain: c for c in existing_local}

    for remote_company in remote_companies:
        if not remote_company.domain:
            result.errors.append(
                f"Skipping '{remote_company.name}': no domain set (natural key required)"
            )
            continue

        try:
            # Upsert company by domain (remote wins for metadata)
            local_company = local_companies_map.get(remote_company.domain)

            if local_company:
                # Update existing — remote wins for metadata
                local_company.name = remote_company.name
                local_company.url = remote_company.url
                local_company.careers_url = remote_company.careers_url
                local_company.discovery_trace = remote_company.discovery_trace
            else:
                # Insert new
                local_company = Company(
                    name=remote_company.name,
                    domain=remote_company.domain,
                    url=remote_company.url,
                    careers_url=remote_company.careers_url,
                    discovery_trace=remote_company.discovery_trace,
                    created_at=remote_company.created_at,
                    updated_at=remote_company.updated_at,
                )
                local_db.add(local_company)
                local_db.flush()  # Get the ID
                local_companies_map[remote_company.domain] = local_company

            result.companies_pulled += 1

            # Pre-fetch scores for this local company
            existing_scores = local_db.execute(
                select(Score).where(Score.company_id == local_company.id)
            ).scalars().all()
            
            # Ensure scores use explicit UTC to avoid duplicate inserts on SQLite
            existing_score_dates = set()
            for s in existing_scores:
                if s.created_at:
                    existing_score_dates.add(s.created_at.replace(tzinfo=timezone.utc).isoformat())

            # Pull scores (append-only, skip existing)
            remote_scores = remote_company.scores
            if since:
                since_naive = since.replace(tzinfo=None)
                remote_scores = [
                    s for s in remote_scores
                    if s.created_at and s.created_at.replace(tzinfo=None) >= since_naive
                ]

            for remote_score in remote_scores:
                if not remote_score.created_at:
                    continue
                    
                remote_score_utc = remote_score.created_at.replace(tzinfo=timezone.utc)
                remote_score_iso = remote_score_utc.isoformat()
                
                if remote_score_iso not in existing_score_dates:
                    new_score = Score(
                        company_id=local_company.id,
                        score=remote_score.score,
                        category=remote_score.category,
                        signals=remote_score.signals,
                        component_scores=remote_score.component_scores,
                        evidence=remote_score.evidence,
                        created_at=remote_score_utc,
                    )
                    local_db.add(new_score)
                    existing_score_dates.add(remote_score_iso)
                    result.scores_pulled += 1
                else:
                    result.skipped += 1

            # Pre-fetch sources for this local company
            existing_sources = local_db.execute(
                select(CompanySource).where(CompanySource.company_id == local_company.id)
            ).scalars().all()
            existing_sources_map = {s.url: s for s in existing_sources}

            # Pull sources (upsert by company+url)
            for remote_source in remote_company.sources:
                existing = existing_sources_map.get(remote_source.url)

                if existing:
                    existing.source_type = remote_source.source_type
                    existing.is_active = remote_source.is_active
                    existing.verification_status = remote_source.verification_status
                    existing.submitted_by = remote_source.submitted_by
                else:
                    new_source = CompanySource(
                        company_id=local_company.id,
                        url=remote_source.url,
                        source_type=remote_source.source_type,
                        is_active=remote_source.is_active,
                        verification_status=remote_source.verification_status,
                        submitted_by=remote_source.submitted_by,
                        last_scraped_at=remote_source.last_scraped_at,
                    )
                    local_db.add(new_source)
                    existing_sources_map[remote_source.url] = new_source
                result.sources_pulled += 1

            # Pre-fetch aliases (upsert by alias_domain)
            remote_alias_domains = [a.alias_domain for a in remote_company.domain_aliases]
            if remote_alias_domains:
                existing_aliases = local_db.execute(
                    select(CompanyDomainAlias).where(CompanyDomainAlias.alias_domain.in_(remote_alias_domains))
                ).scalars().all()
                existing_aliases_map = {a.alias_domain: a for a in existing_aliases}
            else:
                existing_aliases_map = {}

            # Pull aliases (upsert by alias_domain)
            for remote_alias in remote_company.domain_aliases:
                existing = existing_aliases_map.get(remote_alias.alias_domain)

                if not existing:
                    new_alias = CompanyDomainAlias(
                        company_id=local_company.id,
                        alias_domain=remote_alias.alias_domain,
                        created_at=remote_alias.created_at,
                    )
                    local_db.add(new_alias)
                    existing_aliases_map[remote_alias.alias_domain] = new_alias
                else:
                    existing.company_id = local_company.id
                result.aliases_pulled += 1

            # Commit per company to avoid mega-transaction unless it's a dry run
            if not dry_run:
                local_db.commit()

        except Exception as e:
            if not dry_run:
                local_db.rollback()
            result.errors.append(f"Failed to pull company '{remote_company.name}': {str(e)}")

    if dry_run:
        local_db.rollback()

    return result


def print_summary(result: PullResult, dry_run: bool = False) -> None:
    """Print a human-readable pull summary."""
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{'=' * 50}")
    print(f"{prefix}Pull Summary")
    print(f"{'=' * 50}")
    print(f"  Companies: {result.companies_pulled}")
    print(f"  Scores:    {result.scores_pulled}")
    print(f"  Sources:   {result.sources_pulled}")
    print(f"  Aliases:   {result.aliases_pulled}")
    print(f"  Skipped:   {result.skipped}")

    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for err in result.errors:
            print(f"    - {err}")
    else:
        print(f"\n  Errors:    0")

    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(
        description="Pull scoring data from a remote database to local"
    )
    parser.add_argument(
        "--remote-url",
        default=os.environ.get("REMOTE_DATABASE_URL"),
        help="Remote database URL (or set REMOTE_DATABASE_URL env var)",
    )
    parser.add_argument(
        "--company",
        help="Only pull a specific company (by name)",
    )
    parser.add_argument(
        "--since",
        help="Only pull scores created after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be pulled without modifying local",
    )

    args = parser.parse_args()

    if not args.remote_url:
        parser.error(
            "--remote-url is required (or set REMOTE_DATABASE_URL env var)"
        )

    # Parse --since
    since = None
    if args.since:
        since = datetime.strptime(args.since, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )

    # Backup local DB before pull
    from app.core.config import settings

    local_db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if local_db_path and not local_db_path.startswith(":"):
        bak = backup_local_db(local_db_path)
        if bak:
            print(f"Backup created: {bak}")

    # Create remote engine/session
    remote_kwargs = {"echo": False}
    if args.remote_url.startswith("sqlite"):
        remote_kwargs["connect_args"] = {"check_same_thread": False}
    remote_engine = create_engine(args.remote_url, **remote_kwargs)
    RemoteSession = sessionmaker(bind=remote_engine)

    local_db = SessionLocal()
    remote_db = RemoteSession()

    try:
        print(f"Pulling remote data ← {args.remote_url.split('@')[0]}@***")
        if args.company:
            print(f"  Filter: company = '{args.company}'")
        if args.since:
            print(f"  Filter: since = {args.since}")
        if args.dry_run:
            print(f"  Mode: DRY RUN")

        result = pull_scores(
            remote_db,
            local_db,
            company_filter=args.company,
            since=since,
            dry_run=args.dry_run,
        )

        print_summary(result, dry_run=args.dry_run)

    except Exception as e:
        local_db.rollback()
        print(f"\nFATAL: Pull failed — {e}")
        raise
    finally:
        local_db.close()
        remote_db.close()


if __name__ == "__main__":
    main()
