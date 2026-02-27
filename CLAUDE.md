# SignalScore - Agent Instructions

## Test Infrastructure

### Two Test Categories

1. **Stable Tests** - Contract and component tests that validate core business logic boundaries. These should rarely change.
2. **Regular Tests** - Unit, integration, and feature tests that may evolve alongside the codebase.

### Running Tests

```bash
# Backend: all tests
cd execution/backend && pytest -v --ignore=tests/integration

# Backend: stable subset only
cd execution/backend && pytest -m stable -v

# Frontend: all tests
cd execution/frontend && npx vitest run

# Frontend: stable subset only
cd execution/frontend && npm run test:stable
```

### Stable Test Rules

**Do NOT modify stable tests without explicit user confirmation.**

- Backend stable tests are marked with `@pytest.mark.stable` or `pytestmark = pytest.mark.stable`
- Frontend stable tests use the `.stable.test.ts(x)` file naming convention

If a stable test fails after a code change, the code change is likely wrong — investigate the production code first. Only update a stable test after discussing with the user.

### Stable Test Files

**Backend** (46 tests across 6 files + 2 individual markers):
- `tests/test_url_validation.py` - URL normalization contract
- `tests/test_synthesis.py` - Scoring algorithm signal extraction
- `tests/test_domain_rollup.py` - Domain deduplication logic
- `tests/test_ats_detector.py` - ATS link detection contract
- `tests/services/test_scoring.py` - Score calculator contract
- `tests/utils/test_source_detection.py` - Source type detection
- `tests/test_async_scoring.py::test_async_scoring_flow_existing_company` - API: existing company returns 200
- `tests/test_on_demand_scoring.py::test_invalid_url_validation` - API: rejects bad URLs

**Frontend** (37 tests across 3 files):
- `validators.stable.test.ts` - URL validation contract
- `ScoreDisplay.stable.test.tsx` - Score display component rendering
- `CompanyCard.stable.test.tsx` - Company card component rendering

## When to Test

### During a story
Run only the tests related to the story being worked on:
- Run the specific test file(s) that cover the code you're changing
- Add or update regular (non-stable) tests to cover new behavior
- When adding a new API endpoint: add a happy-path test and an error-case test
- When modifying scoring logic: add new cases if the change introduces new signal types

### Before deployment (story batch, minor release, or major release)
Run the full suites and verify everything is green:
```bash
# All backend tests
cd execution/backend && pytest -v --ignore=tests/integration

# All frontend tests
cd execution/frontend && npx vitest run
```
- If a **stable** test fails, investigate the production code first — the test is likely correct
- All failures must be resolved before deploying

## Conventions

- **Backend**: Python 3.11+, FastAPI, pytest, pytest-asyncio (async_mode=auto)
- **Frontend**: Next.js 14, Vitest (not Jest), React Testing Library
- **Test isolation**: In-memory SQLite with `StaticPool` for backend; jsdom environment for frontend
- **Mocking**: Use `vi.mock()` / `vi.fn()` in frontend (never `jest.mock()`)
- **DB overrides**: Always set `app.dependency_overrides[get_db]` inside fixtures (not at module level) to avoid cross-test contamination
