"""Tests for pull_scores CLI script.

Uses two in-memory SQLite databases to simulate remote → local pull.
"""

import os
import shutil
import tempfile
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.company import Company, Score, CompanySource, CompanyDomainAlias
from app.models.enums import AIReadinessCategory


def make_engine():
    """Create a fresh in-memory SQLite engine."""
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def local_session():
    """Local database session (target for pull)."""
    engine = make_engine()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def remote_session():
    """Remote database session (source for pull)."""
    engine = make_engine()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def seed_company(session, name="Acme Corp", domain="acme.com", **kwargs):
    """Helper to seed a company with scores and sources."""
    now = datetime.now(timezone.utc)
    company = Company(
        name=name,
        domain=domain,
        url=kwargs.get("url", f"https://{domain}"),
        careers_url=kwargs.get("careers_url", f"https://{domain}/careers"),
        created_at=now,
        updated_at=now,
    )
    session.add(company)
    session.flush()

    # Add scores
    for i, score_val in enumerate(kwargs.get("scores", [75.0])):
        score = Score(
            company_id=company.id,
            score=score_val,
            category=AIReadinessCategory.OPERATIONAL,
            signals={"ai_keywords": 5, "tool_stack": ["pytorch"]},
            component_scores={"tech": 80, "adoption": 70},
            evidence=["https://example.com/evidence"],
            created_at=now - timedelta(days=i),
        )
        session.add(score)

    # Add sources
    for src_url in kwargs.get("sources", [f"https://{domain}/careers"]):
        source = CompanySource(
            company_id=company.id,
            url=src_url,
            source_type="careers_page",
            is_active=True,
            verification_status="verified",
            last_scraped_at=now,
        )
        session.add(source)

    # Add aliases
    for alias in kwargs.get("aliases", []):
        alias_obj = CompanyDomainAlias(
            company_id=company.id,
            alias_domain=alias,
            created_at=now,
        )
        session.add(alias_obj)

    session.commit()
    return company


# ── Import the module under test ──────────────────────────────────────

from scripts.pull_scores import pull_scores, PullResult


# ── AC1: Pull Command ─────────────────────────────────────────────────


class TestPullCommand:
    """AC1: Pull all companies, scores, sources, and aliases from remote."""

    def test_pull_single_company(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com")

        result = pull_scores(remote_session, local_session)

        assert result.companies_pulled == 1
        local_companies = local_session.execute(select(Company)).scalars().all()
        assert len(local_companies) == 1
        assert local_companies[0].domain == "acme.com"
        assert local_companies[0].name == "Acme Corp"

    def test_pull_with_scores(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com", scores=[80.0, 75.0])

        result = pull_scores(remote_session, local_session)

        assert result.scores_pulled == 2
        local_scores = local_session.execute(select(Score)).scalars().all()
        assert len(local_scores) == 2

    def test_pull_with_sources(self, local_session, remote_session):
        seed_company(
            remote_session,
            "Acme Corp",
            "acme.com",
            sources=["https://acme.com/careers", "https://acme.com/blog"],
        )

        result = pull_scores(remote_session, local_session)

        assert result.sources_pulled == 2
        local_sources = local_session.execute(select(CompanySource)).scalars().all()
        assert len(local_sources) == 2

    def test_pull_with_aliases(self, local_session, remote_session):
        seed_company(
            remote_session,
            "Acme Corp",
            "acme.com",
            aliases=["acmecorp.io", "acme.dev"],
        )

        result = pull_scores(remote_session, local_session)

        assert result.aliases_pulled == 2
        local_aliases = (
            local_session.execute(select(CompanyDomainAlias)).scalars().all()
        )
        assert len(local_aliases) == 2

    def test_pull_multiple_companies(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com")
        seed_company(remote_session, "Beta Inc", "beta.io")

        result = pull_scores(remote_session, local_session)

        assert result.companies_pulled == 2
        local_companies = local_session.execute(select(Company)).scalars().all()
        assert len(local_companies) == 2

    def test_pull_preserves_foreign_keys(self, local_session, remote_session):
        """AC4-adjacent: FK relationships preserved on pull."""
        seed_company(remote_session, "Acme Corp", "acme.com", scores=[80.0])

        pull_scores(remote_session, local_session)

        local_company = local_session.execute(
            select(Company).where(Company.domain == "acme.com")
        ).scalar_one()
        local_score = local_session.execute(select(Score)).scalar_one()
        assert local_score.company_id == local_company.id


# ── AC2: Selective Pull ──────────────────────────────────────────────


class TestSelectivePull:
    """AC2: Filter by --company or --since."""

    def test_filter_by_company_name(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com")
        seed_company(remote_session, "Beta Inc", "beta.io")

        result = pull_scores(
            remote_session, local_session, company_filter="Acme Corp"
        )

        assert result.companies_pulled == 1
        local_companies = local_session.execute(select(Company)).scalars().all()
        assert len(local_companies) == 1
        assert local_companies[0].name == "Acme Corp"

    def test_filter_by_since_date(self, local_session, remote_session):
        now = datetime.now(timezone.utc)
        old = now - timedelta(days=30)

        # Company with old score only
        c1 = seed_company(remote_session, "Old Corp", "old.com", scores=[])
        old_score = Score(
            company_id=c1.id,
            score=50.0,
            category=AIReadinessCategory.LAGGING,
            signals={"ai_keywords": 1},
            component_scores={"tech": 30},
            evidence=[],
            created_at=old,
        )
        remote_session.add(old_score)

        # Company with recent score
        c2 = seed_company(remote_session, "New Corp", "new.com", scores=[])
        new_score = Score(
            company_id=c2.id,
            score=90.0,
            category=AIReadinessCategory.LEADING,
            signals={"ai_keywords": 10},
            component_scores={"tech": 95},
            evidence=[],
            created_at=now,
        )
        remote_session.add(new_score)
        remote_session.commit()

        since = now - timedelta(days=7)
        result = pull_scores(remote_session, local_session, since=since)

        # Both companies pulled, but only recent score
        local_scores = local_session.execute(select(Score)).scalars().all()
        assert len(local_scores) == 1
        assert local_scores[0].score == 90.0


# ── AC3: Upsert Semantics ───────────────────────────────────────────


class TestUpsertSemantics:
    """AC3: Upsert without duplication; scores are append-only."""

    def test_company_updated_not_duplicated(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com")

        # First pull
        pull_scores(remote_session, local_session)

        # Modify remotely
        remote_company = remote_session.execute(
            select(Company).where(Company.domain == "acme.com")
        ).scalar_one()
        remote_company.careers_url = "https://acme.com/jobs"
        remote_session.commit()

        # Second pull
        pull_scores(remote_session, local_session)

        local_companies = local_session.execute(select(Company)).scalars().all()
        assert len(local_companies) == 1  # Not duplicated
        assert local_companies[0].careers_url == "https://acme.com/jobs"

    def test_scores_appended_not_duplicated(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com", scores=[80.0])

        # First pull
        pull_scores(remote_session, local_session)
        assert len(local_session.execute(select(Score)).scalars().all()) == 1

        # Add new score remotely
        remote_company = remote_session.execute(
            select(Company).where(Company.domain == "acme.com")
        ).scalar_one()
        new_score = Score(
            company_id=remote_company.id,
            score=85.0,
            category=AIReadinessCategory.LEADING,
            signals={"ai_keywords": 8},
            component_scores={"tech": 90},
            evidence=[],
            created_at=datetime.now(timezone.utc),
        )
        remote_session.add(new_score)
        remote_session.commit()

        # Second pull
        pull_scores(remote_session, local_session)

        local_scores = local_session.execute(select(Score)).scalars().all()
        assert len(local_scores) == 2  # Appended, not duplicated

    def test_sources_upserted_not_duplicated(self, local_session, remote_session):
        seed_company(
            remote_session,
            "Acme Corp",
            "acme.com",
            sources=["https://acme.com/careers"],
        )

        pull_scores(remote_session, local_session)
        pull_scores(remote_session, local_session)

        local_sources = local_session.execute(select(CompanySource)).scalars().all()
        assert len(local_sources) == 1  # Not duplicated


# ── AC4: Conflict Handling ─────────────────────────────────────────


class TestConflictHandling:
    """AC4: Remote wins for metadata; scores merge (append both)."""

    def test_remote_wins_for_metadata(self, local_session, remote_session):
        """Remote version of company metadata should overwrite local."""
        # Local has old data
        seed_company(local_session, "Acme Old", "acme.com",
                     url="https://old.acme.com")
        # Remote has newer data
        seed_company(remote_session, "Acme New", "acme.com",
                     url="https://new.acme.com")

        pull_scores(remote_session, local_session)

        local_company = local_session.execute(
            select(Company).where(Company.domain == "acme.com")
        ).scalar_one()
        assert local_company.name == "Acme New"
        assert local_company.url == "https://new.acme.com"

    def test_local_scores_preserved_on_pull(self, local_session, remote_session):
        """Local scores should not be deleted when pulling remote scores."""
        now = datetime.now(timezone.utc)

        # Local company with a local-only score
        local_company = seed_company(local_session, "Acme Corp", "acme.com", scores=[])
        local_score = Score(
            company_id=local_company.id,
            score=70.0,
            category=AIReadinessCategory.OPERATIONAL,
            signals={"ai_keywords": 3},
            component_scores={"tech": 60},
            evidence=[],
            created_at=now - timedelta(hours=1),
        )
        local_session.add(local_score)
        local_session.commit()

        # Remote company with a different score
        remote_company = seed_company(remote_session, "Acme Corp", "acme.com", scores=[])
        remote_score = Score(
            company_id=remote_company.id,
            score=90.0,
            category=AIReadinessCategory.LEADING,
            signals={"ai_keywords": 10},
            component_scores={"tech": 95},
            evidence=[],
            created_at=now,
        )
        remote_session.add(remote_score)
        remote_session.commit()

        pull_scores(remote_session, local_session)

        local_scores = local_session.execute(select(Score)).scalars().all()
        score_values = sorted([s.score for s in local_scores])
        assert len(local_scores) == 2  # Both preserved
        assert score_values == [70.0, 90.0]


# ── AC5: Dry Run ─────────────────────────────────────────────────────


class TestDryRun:
    """AC5: --dry-run shows what would be pulled without modifying local."""

    def test_dry_run_does_not_modify_local(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com")

        result = pull_scores(remote_session, local_session, dry_run=True)

        assert result.companies_pulled == 1
        # Local should be untouched
        local_companies = local_session.execute(select(Company)).scalars().all()
        assert len(local_companies) == 0


# ── AC6: Pull Summary ───────────────────────────────────────────────


class TestPullSummary:
    """AC6: Output summary of what was pulled."""

    def test_summary_includes_all_counts(self, local_session, remote_session):
        seed_company(
            remote_session,
            "Acme Corp",
            "acme.com",
            scores=[80.0, 75.0],
            sources=["https://acme.com/careers", "https://acme.com/blog"],
            aliases=["acmecorp.io"],
        )

        result = pull_scores(remote_session, local_session)

        assert result.companies_pulled == 1
        assert result.scores_pulled == 2
        assert result.sources_pulled == 2
        assert result.aliases_pulled == 1
        assert result.errors == []

    def test_skipped_count_for_existing(self, local_session, remote_session):
        seed_company(remote_session, "Acme Corp", "acme.com", scores=[80.0])

        # First pull
        pull_scores(remote_session, local_session)

        # Second pull — score already exists
        result = pull_scores(remote_session, local_session)
        assert result.scores_pulled == 0
        assert result.skipped == 1


# ── Backup Tests ─────────────────────────────────────────────────────


class TestBackup:
    """AC-adjacent: Auto-backup of local DB before pull."""

    def test_backup_creates_copy(self):
        """backup_local_db should create a .bak copy."""
        from scripts.pull_scores import backup_local_db

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            f.write(b"test database content")
            db_path = f.name

        try:
            bak_path = backup_local_db(db_path)
            assert os.path.exists(bak_path)
            assert bak_path.endswith(".bak")
            with open(bak_path, "rb") as bak:
                assert bak.read() == b"test database content"
        finally:
            os.unlink(db_path)
            if os.path.exists(bak_path):
                os.unlink(bak_path)

    def test_no_backup_for_in_memory(self):
        """In-memory databases (used in tests) should not attempt backup."""
        from scripts.pull_scores import backup_local_db

        result = backup_local_db(":memory:")
        assert result is None


# ── CLI & Main Tests ──────────────────────────────────────────────────

from io import StringIO
import sys
from unittest.mock import patch
from scripts.pull_scores import print_summary, main


class TestCLIAndHelpers:
    """Tests for CLI arguments, environment variables, and print helpers."""

    def test_print_summary(self):
        result = PullResult(companies_pulled=1, scores_pulled=2, skipped=1, errors=["Timeout"])
        captured = StringIO()
        sys.stdout = captured
        try:
            print_summary(result, dry_run=True)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "[DRY RUN]" in output
        assert "Companies: 1" in output
        assert "Scores:    2" in output
        assert "Skipped:   1" in output
        assert "Timeout" in output

    @patch("scripts.pull_scores.pull_scores")
    @patch("scripts.pull_scores.SessionLocal")
    @patch("scripts.pull_scores.create_engine")
    @patch("scripts.pull_scores.backup_local_db")
    @patch("app.core.config.settings")
    @patch("sys.argv", ["scripts.pull_scores", "--remote-url", "sqlite:///:memory:", "--company", "Acme", "--since", "2026-02-01"])
    def test_main_cli_args(self, mock_settings, mock_backup, mock_create_engine, mock_session_local, mock_pull_scores):
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        mock_pull_scores.return_value = PullResult()

        main()

        mock_pull_scores.assert_called_once()
        kwargs = mock_pull_scores.call_args.kwargs
        assert kwargs["company_filter"] == "Acme"
        assert kwargs["since"].year == 2026
        assert kwargs["since"].month == 2
        assert kwargs["since"].day == 1
        assert kwargs["dry_run"] is False

    @patch("scripts.pull_scores.pull_scores")
    @patch("scripts.pull_scores.SessionLocal")
    @patch("scripts.pull_scores.create_engine")
    @patch("scripts.pull_scores.backup_local_db")
    @patch("app.core.config.settings")
    @patch("sys.argv", ["scripts.pull_scores", "--remote-url", "sqlite:///:memory:"])
    def test_main_transaction_rollback(self, mock_settings, mock_backup, mock_create_engine, mock_session_local, mock_pull_scores):
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        mock_pull_scores.side_effect = Exception("Simulated fatal error")

        with pytest.raises(Exception, match="Simulated fatal error"):
            main()
