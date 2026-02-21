"""Tests for push_scores CLI script.

Uses two in-memory SQLite databases to simulate local → remote push.
"""

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
    """Local database session with test data."""
    engine = make_engine()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def remote_session():
    """Remote database session (empty)."""
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

from scripts.push_scores import push_scores, PushResult


# ── AC1: Push Command ─────────────────────────────────────────────────


class TestPushCommand:
    """AC1: Push all companies, scores, sources, and aliases to remote."""

    def test_push_single_company(self, local_session, remote_session):
        seed_company(local_session, "Acme Corp", "acme.com")

        result = push_scores(local_session, remote_session)

        assert result.companies_pushed == 1
        remote_companies = remote_session.execute(select(Company)).scalars().all()
        assert len(remote_companies) == 1
        assert remote_companies[0].domain == "acme.com"
        assert remote_companies[0].name == "Acme Corp"

    def test_push_with_scores(self, local_session, remote_session):
        seed_company(local_session, "Acme Corp", "acme.com", scores=[80.0, 75.0])

        result = push_scores(local_session, remote_session)

        assert result.scores_pushed == 2
        remote_scores = remote_session.execute(select(Score)).scalars().all()
        assert len(remote_scores) == 2

    def test_push_with_sources(self, local_session, remote_session):
        seed_company(
            local_session,
            "Acme Corp",
            "acme.com",
            sources=["https://acme.com/careers", "https://acme.com/blog"],
        )

        result = push_scores(local_session, remote_session)

        assert result.sources_pushed == 2
        remote_sources = remote_session.execute(select(CompanySource)).scalars().all()
        assert len(remote_sources) == 2

    def test_push_with_aliases(self, local_session, remote_session):
        seed_company(
            local_session,
            "Acme Corp",
            "acme.com",
            aliases=["acmecorp.io", "acme.dev"],
        )

        result = push_scores(local_session, remote_session)

        assert result.aliases_pushed == 2
        remote_aliases = (
            remote_session.execute(select(CompanyDomainAlias)).scalars().all()
        )
        assert len(remote_aliases) == 2

    def test_push_multiple_companies(self, local_session, remote_session):
        seed_company(local_session, "Acme Corp", "acme.com")
        seed_company(local_session, "Beta Inc", "beta.io")

        result = push_scores(local_session, remote_session)

        assert result.companies_pushed == 2
        remote_companies = remote_session.execute(select(Company)).scalars().all()
        assert len(remote_companies) == 2

    def test_push_preserves_foreign_keys(self, local_session, remote_session):
        """AC4: FK relationships preserved."""
        seed_company(local_session, "Acme Corp", "acme.com", scores=[80.0])

        push_scores(local_session, remote_session)

        remote_company = remote_session.execute(
            select(Company).where(Company.domain == "acme.com")
        ).scalar_one()
        remote_score = remote_session.execute(select(Score)).scalar_one()
        assert remote_score.company_id == remote_company.id


# ── AC2: Selective Push ──────────────────────────────────────────────


class TestSelectivePush:
    """AC2: Filter by --company or --since."""

    def test_filter_by_company_name(self, local_session, remote_session):
        seed_company(local_session, "Acme Corp", "acme.com")
        seed_company(local_session, "Beta Inc", "beta.io")

        result = push_scores(
            local_session, remote_session, company_filter="Acme Corp"
        )

        assert result.companies_pushed == 1
        remote_companies = remote_session.execute(select(Company)).scalars().all()
        assert len(remote_companies) == 1
        assert remote_companies[0].name == "Acme Corp"

    def test_filter_by_since_date(self, local_session, remote_session):
        now = datetime.now(timezone.utc)
        old = now - timedelta(days=30)

        # Company with old score only
        c1 = seed_company(local_session, "Old Corp", "old.com", scores=[])
        old_score = Score(
            company_id=c1.id,
            score=50.0,
            category=AIReadinessCategory.LAGGING,
            signals={"ai_keywords": 1},
            component_scores={"tech": 30},
            evidence=[],
            created_at=old,
        )
        local_session.add(old_score)

        # Company with recent score
        c2 = seed_company(local_session, "New Corp", "new.com", scores=[])
        new_score = Score(
            company_id=c2.id,
            score=90.0,
            category=AIReadinessCategory.LEADING,
            signals={"ai_keywords": 10},
            component_scores={"tech": 95},
            evidence=[],
            created_at=now,
        )
        local_session.add(new_score)
        local_session.commit()

        since = now - timedelta(days=7)
        result = push_scores(local_session, remote_session, since=since)

        # Both companies pushed (they have sources), but only recent score pushed
        remote_scores = remote_session.execute(select(Score)).scalars().all()
        assert len(remote_scores) == 1
        assert remote_scores[0].score == 90.0


# ── AC3: Upsert Semantics ───────────────────────────────────────────


class TestUpsertSemantics:
    """AC3: Upsert without duplication; scores are append-only."""

    def test_company_updated_not_duplicated(self, local_session, remote_session):
        seed_company(local_session, "Acme Corp", "acme.com")

        # First push
        push_scores(local_session, remote_session)

        # Modify locally
        local_company = local_session.execute(
            select(Company).where(Company.domain == "acme.com")
        ).scalar_one()
        local_company.careers_url = "https://acme.com/jobs"
        local_session.commit()

        # Second push
        push_scores(local_session, remote_session)

        remote_companies = remote_session.execute(select(Company)).scalars().all()
        assert len(remote_companies) == 1  # Not duplicated
        assert remote_companies[0].careers_url == "https://acme.com/jobs"

    def test_scores_appended_not_duplicated(self, local_session, remote_session):
        seed_company(local_session, "Acme Corp", "acme.com", scores=[80.0])

        # First push
        push_scores(local_session, remote_session)
        assert remote_session.execute(select(Score)).scalars().all().__len__() == 1

        # Add new score locally
        local_company = local_session.execute(
            select(Company).where(Company.domain == "acme.com")
        ).scalar_one()
        new_score = Score(
            company_id=local_company.id,
            score=85.0,
            category=AIReadinessCategory.LEADING,
            signals={"ai_keywords": 8},
            component_scores={"tech": 90},
            evidence=[],
            created_at=datetime.now(timezone.utc),
        )
        local_session.add(new_score)
        local_session.commit()

        # Second push
        push_scores(local_session, remote_session)

        remote_scores = remote_session.execute(select(Score)).scalars().all()
        assert len(remote_scores) == 2  # Appended, not duplicated

    def test_sources_upserted_not_duplicated(self, local_session, remote_session):
        seed_company(
            local_session,
            "Acme Corp",
            "acme.com",
            sources=["https://acme.com/careers"],
        )

        push_scores(local_session, remote_session)
        push_scores(local_session, remote_session)

        remote_sources = remote_session.execute(select(CompanySource)).scalars().all()
        assert len(remote_sources) == 1  # Not duplicated


# ── AC5: Dry Run ─────────────────────────────────────────────────────


class TestDryRun:
    """AC5: --dry-run shows what would be pushed without modifying remote."""

    def test_dry_run_does_not_modify_remote(self, local_session, remote_session):
        seed_company(local_session, "Acme Corp", "acme.com")

        result = push_scores(local_session, remote_session, dry_run=True)

        assert result.companies_pushed == 1
        # Remote should be untouched
        remote_companies = remote_session.execute(select(Company)).scalars().all()
        assert len(remote_companies) == 0


# ── AC6: Push Summary ───────────────────────────────────────────────


class TestPushSummary:
    """AC6: Output summary of what was pushed."""

    def test_summary_includes_all_counts(self, local_session, remote_session):
        seed_company(
            local_session,
            "Acme Corp",
            "acme.com",
            scores=[80.0, 75.0],
            sources=["https://acme.com/careers", "https://acme.com/blog"],
            aliases=["acmecorp.io"],
        )

        result = push_scores(local_session, remote_session)

        assert result.companies_pushed == 1
        assert result.scores_pushed == 2
        assert result.sources_pushed == 2
        assert result.aliases_pushed == 1
        assert result.errors == []
