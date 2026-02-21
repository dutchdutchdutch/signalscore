"""Push local scoring data (companies, scores, sources, aliases) to a remote database.

Usage:
    python -m scripts.push_scores --remote-url "postgresql+pg8000://..."
    python -m scripts.push_scores --remote-url "..." --company "Google"
    python -m scripts.push_scores --remote-url "..." --since 2026-02-01
    python -m scripts.push_scores --remote-url "..." --dry-run

Sync protocol:
  - Natural key: company.domain (stable across environments)
  - Companies: upsert by domain
  - Scores: append-only (skip if same company+created_at exists)
  - Sources: upsert by company+url
  - Aliases: upsert by alias_domain
  - All operations in a single transaction
"""

import argparse
import os
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
class PushResult:
    """Summary of a push operation."""

    companies_pushed: int = 0
    scores_pushed: int = 0
    sources_pushed: int = 0
    aliases_pushed: int = 0
    errors: list[str] = field(default_factory=list)


def push_scores(
    local_db: Session,
    remote_db: Session,
    *,
    company_filter: Optional[str] = None,
    since: Optional[datetime] = None,
    dry_run: bool = False,
) -> PushResult:
    """Push scoring data from local to remote database.

    Args:
        local_db: Session connected to the local (source) database.
        remote_db: Session connected to the remote (target) database.
        company_filter: If set, only push companies matching this name.
        since: If set, only push scores created after this datetime.
        dry_run: If True, compute what would be pushed but don't commit.

    Returns:
        PushResult with counts of pushed records.
    """
    result = PushResult()

    # Load companies from local
    stmt = select(Company)
    if company_filter:
        stmt = stmt.where(Company.name == company_filter)
    local_companies = local_db.execute(stmt).scalars().all()

    # Pre-fetch all needed remote companies by domain
    remote_companies_map = {}
    if local_companies:
        domains = [c.domain for c in local_companies if c.domain]
        # fetch existing companies
        existing_remote = remote_db.execute(
            select(Company).where(Company.domain.in_(domains))
        ).scalars().all()
        remote_companies_map = {c.domain: c for c in existing_remote}

    for local_company in local_companies:
        if not local_company.domain:
            result.errors.append(
                f"Skipping '{local_company.name}': no domain set (natural key required)"
            )
            continue

        try:
            remote_company = remote_companies_map.get(local_company.domain)

            if remote_company:
                # Update existing
                remote_company.name = local_company.name
                remote_company.url = local_company.url
                remote_company.careers_url = local_company.careers_url
                remote_company.discovery_trace = local_company.discovery_trace
            else:
                # Insert new
                remote_company = Company(
                    name=local_company.name,
                    domain=local_company.domain,
                    url=local_company.url,
                    careers_url=local_company.careers_url,
                    discovery_trace=local_company.discovery_trace,
                    created_at=local_company.created_at,
                    updated_at=local_company.updated_at,
                )
                remote_db.add(remote_company)
                remote_db.flush()  # Get the ID
                remote_companies_map[local_company.domain] = remote_company

            result.companies_pushed += 1

            # Pre-fetch scores for this remote company
            existing_scores = remote_db.execute(
                select(Score).where(Score.company_id == remote_company.id)
            ).scalars().all()
            # Ensure scores use explicit UTC to avoid duplicate inserts on Postgres
            existing_score_dates = set()
            for s in existing_scores:
                if s.created_at:
                    existing_score_dates.add(s.created_at.replace(tzinfo=timezone.utc).isoformat())

            # Push scores (append-only)
            local_scores = local_company.scores
            if since:
                # Handle both tz-aware and tz-naive datetimes (SQLite stores naive)
                since_naive = since.replace(tzinfo=None)
                local_scores = [
                    s for s in local_scores
                    if s.created_at and s.created_at.replace(tzinfo=None) >= since_naive
                ]

            for local_score in local_scores:
                if not local_score.created_at:
                    continue
                    
                local_score_utc = local_score.created_at.replace(tzinfo=timezone.utc)
                local_score_iso = local_score_utc.isoformat()
                
                if local_score_iso not in existing_score_dates:
                    new_score = Score(
                        company_id=remote_company.id,
                        score=local_score.score,
                        category=local_score.category,
                        signals=local_score.signals,
                        component_scores=local_score.component_scores,
                        evidence=local_score.evidence,
                        created_at=local_score_utc,
                    )
                    remote_db.add(new_score)
                    # Add to set so we don't insert duplicate if local data has them
                    existing_score_dates.add(local_score_iso)
                    result.scores_pushed += 1

            # Pre-fetch sources for this remote company
            existing_sources = remote_db.execute(
                select(CompanySource).where(CompanySource.company_id == remote_company.id)
            ).scalars().all()
            existing_sources_map = {s.url: s for s in existing_sources}

            # Push sources (upsert by company+url)
            for local_source in local_company.sources:
                # Skip URLs that exceed Postgres VARCHAR(500) limit
                if len(local_source.url) > 500:
                    result.errors.append(
                        f"Skipping source for '{local_company.name}': URL too long ({len(local_source.url)} chars)"
                    )
                    continue

                existing = existing_sources_map.get(local_source.url)

                if existing:
                    existing.source_type = local_source.source_type
                    existing.is_active = local_source.is_active
                    existing.verification_status = local_source.verification_status
                    existing.submitted_by = local_source.submitted_by
                else:
                    new_source = CompanySource(
                        company_id=remote_company.id,
                        url=local_source.url,
                        source_type=local_source.source_type,
                        is_active=local_source.is_active,
                        verification_status=local_source.verification_status,
                        submitted_by=local_source.submitted_by,
                        last_scraped_at=local_source.last_scraped_at,
                    )
                    remote_db.add(new_source)
                    existing_sources_map[local_source.url] = new_source
                result.sources_pushed += 1

            # Pre-fetch aliases (upsert by alias_domain) - these are globally unique usually but bound here
            local_alias_domains = [a.alias_domain for a in local_company.domain_aliases]
            if local_alias_domains:
                existing_aliases = remote_db.execute(
                    select(CompanyDomainAlias).where(CompanyDomainAlias.alias_domain.in_(local_alias_domains))
                ).scalars().all()
                existing_aliases_map = {a.alias_domain: a for a in existing_aliases}
            else:
                existing_aliases_map = {}

            for local_alias in local_company.domain_aliases:
                existing = existing_aliases_map.get(local_alias.alias_domain)

                if not existing:
                    new_alias = CompanyDomainAlias(
                        company_id=remote_company.id,
                        alias_domain=local_alias.alias_domain,
                        created_at=local_alias.created_at,
                    )
                    remote_db.add(new_alias)
                    existing_aliases_map[local_alias.alias_domain] = new_alias
                else:
                    existing.company_id = remote_company.id
                result.aliases_pushed += 1

            # Commit per company to avoid mega-transaction unless it's a dry run
            if not dry_run:
                remote_db.commit()

        except Exception as e:
            if not dry_run:
                remote_db.rollback()
            result.errors.append(f"Failed to push company '{local_company.name}': {str(e)}")

    if dry_run:
        remote_db.rollback()

    return result


def print_summary(result: PushResult, dry_run: bool = False) -> None:
    """Print a human-readable push summary."""
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{'=' * 50}")
    print(f"{prefix}Push Summary")
    print(f"{'=' * 50}")
    print(f"  Companies: {result.companies_pushed}")
    print(f"  Scores:    {result.scores_pushed}")
    print(f"  Sources:   {result.sources_pushed}")
    print(f"  Aliases:   {result.aliases_pushed}")

    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for err in result.errors:
            print(f"    - {err}")
    else:
        print(f"\n  Errors:    0")

    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(
        description="Push local scoring data to a remote database"
    )
    parser.add_argument(
        "--remote-url",
        default=os.environ.get("REMOTE_DATABASE_URL"),
        help="Remote database URL (or set REMOTE_DATABASE_URL env var)",
    )
    parser.add_argument(
        "--company",
        help="Only push a specific company (by name)",
    )
    parser.add_argument(
        "--since",
        help="Only push scores created after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be pushed without modifying remote",
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

    # Create remote engine/session, ensure tables exist
    remote_kwargs = {"echo": False}
    if args.remote_url.startswith("sqlite"):
        remote_kwargs["connect_args"] = {"check_same_thread": False}
    remote_engine = create_engine(args.remote_url, **remote_kwargs)
    Base.metadata.create_all(bind=remote_engine)
    RemoteSession = sessionmaker(bind=remote_engine)

    local_db = SessionLocal()
    remote_db = RemoteSession()

    try:
        print(f"Pushing local data → {args.remote_url.split('@')[0]}@***")
        if args.company:
            print(f"  Filter: company = '{args.company}'")
        if args.since:
            print(f"  Filter: since = {args.since}")
        if args.dry_run:
            print(f"  Mode: DRY RUN")

        result = push_scores(
            local_db,
            remote_db,
            company_filter=args.company,
            since=since,
            dry_run=args.dry_run,
        )

        print_summary(result, dry_run=args.dry_run)

    except Exception as e:
        remote_db.rollback()
        print(f"\nFATAL: Push failed — {e}")
        raise
    finally:
        local_db.close()
        remote_db.close()


if __name__ == "__main__":
    main()
