"""Scripted 18-exchange coding-assistant session with two objective traps.

Phases: exploration -> debugging -> rename -> long detour -> duplicate-function trap -> renamed-API trap.
Each exchange is (user message, scripted assistant reply). Replies are fixed so the demo is fully
deterministic: it checks *what context reaches the model*, never model output quality.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Trap:
    name: str
    exchange: int  # 1-based exchange whose user message springs the trap
    required: str  # must appear in the assembled context
    stale: str | None  # if present in context, must be marked stale/superseded
    planted_at: int  # exchange where the evidence was planted
    description: str


EXCHANGES: list[tuple[str, str]] = [
    # 1 - exploration
    (
        "Walk me through how the task tracker backend is structured before we change anything.",
        "The backend is a small Flask app. `app/models.py` defines `Task` and `User` with SQLAlchemy, "
        "`app/api.py` exposes the REST routes, and `app/services/` holds query helpers. Tasks belong to "
        "an owner via `Task.owner_id`, and due dates are stored as UTC datetimes.",
    ),
    # 2 - helpers planted (duplicate-function trap evidence; original signature for rename trap)
    (
        "Write a helper to fetch a user's open tasks and a helper to format due dates for display.",
        "Added both to `app/services/tasks.py`:\n"
        "```python\n"
        "def get_user_tasks(user_id, include_done=False):\n"
        "    q = Task.query.filter_by(owner_id=user_id)\n"
        "    return q.all() if include_done else q.filter_by(done=False).all()\n\n"
        "def format_due_date(dt, tz='UTC'):\n"
        "    local = dt.astimezone(ZoneInfo(tz))\n"
        "    return local.strftime('%a %d %b, %H:%M')\n"
        "```",
    ),
    # 3 - exploration
    (
        "How does the API serialize tasks right now?",
        "`app/api.py` calls `task_to_dict(task)` which returns id, title, done and the raw ISO due date. "
        "The frontend formats dates itself at the moment.",
    ),
    # 4 - debugging
    (
        "The dashboard view crashes with KeyError: 'owner' when I open it. Here is the traceback: "
        "File app/views/dashboard.py, line 41, in render_dashboard: tasks = group_by_owner(rows)['owner'].",
        "`group_by_owner` returns a dict keyed by owner id, not by the string 'owner'. Line 41 should be "
        "`tasks = group_by_owner(rows).get(current_user.id, [])`.",
    ),
    # 5 - debugging
    (
        "That fixed the crash but the dashboard now shows an empty list even though I have tasks. Debug it?",
        "`rows` comes from a query filtered on `Task.done == True`, so only finished tasks are grouped. "
        "Flip the filter to `Task.done.is_(False)` in `load_rows()`.",
    ),
    # 6 - debugging
    (
        "Still failing: the test test_dashboard_lists_open_tasks fails with AssertionError: 0 != 3.",
        "The fixture creates tasks for `user_a` but the test client logs in as `user_b`. Use the "
        "`logged_in_as(user_a)` fixture in that test.",
    ),
    # 7 - debugging resolved
    (
        "Great, tests pass now. Thanks.",
        "Good. The dashboard bug was the inverted done filter plus the wrong fixture user.",
    ),
    # 8 - refactor discussion
    (
        "Our auth layer only gives us `uid` now, the old `user_id` naming is gone everywhere else.",
        "Then the service helpers should follow the same naming so callers do not have to translate.",
    ),
    # 9 - RENAME (renamed-API trap evidence)
    (
        "Rename the parameter user_id to uid in get_user_tasks to match the auth layer.",
        "Done:\n"
        "```python\n"
        "def get_user_tasks(uid, include_done=False):\n"
        "    q = Task.query.filter_by(owner_id=uid)\n"
        "    return q.all() if include_done else q.filter_by(done=False).all()\n"
        "```\n"
        "All three internal callers were updated to pass `uid=`.",
    ),
    # 10-15 - long detour (CI, Docker, docs, logging, deployment)
    (
        "Switching gears: let's set up continuous integration. We use GitHub Actions and need pytest on every push.",
        "Created `.github/workflows/ci.yml`: it checks out the repo, sets up Python 3.12 with pip caching, "
        "installs `requirements-dev.txt`, runs `ruff check .` and then `pytest -q --maxfail=1`. Pull requests "
        "to main require the `ci / test` job to pass before merging, and the workflow uploads the junit XML "
        "report as an artifact so failures are easy to inspect from the Actions tab.",
    ),
    (
        "Add a Dockerfile so the app runs the same way locally and in staging.",
        "Added a two-stage Dockerfile: a builder stage installs wheels into /wheels from requirements.txt, "
        "and the runtime stage is python:3.12-slim with a non-root `app` user, copies the wheels, installs "
        "them offline and runs `gunicorn -w 4 -b 0.0.0.0:8000 'app:create_app()'`. A .dockerignore keeps "
        "the virtualenv, caches and the local SQLite database out of the build context.",
    ),
    (
        "Write a docker compose file with postgres and the app for local development.",
        "`compose.yaml` defines `db` (postgres:16 with a named volume and a healthcheck using pg_isready) and "
        "`web` (built from the Dockerfile, depends_on db with condition service_healthy, env from .env, port "
        "8000 published, source mounted for live reload with FLASK_DEBUG=1). `make dev` wraps `docker compose up --build`.",
    ),
    (
        "Update the README with setup instructions for new contributors.",
        "README now has Prerequisites (Docker, make, Python 3.12 for tooling), Quick start (`cp .env.example .env`, "
        "`make dev`, open http://localhost:8000), Running tests (`make test` runs pytest inside the web container), "
        "Linting (`make lint`), and a Troubleshooting section covering port 5432 conflicts and stale volumes.",
    ),
    (
        "Configure structured logging so staging logs are JSON.",
        "Added `app/logging.py` with a dictConfig that uses python-json-logger in staging and production and a "
        "plain console formatter locally, keyed on APP_ENV. Every record carries request_id from a before_request "
        "hook, and gunicorn's access log is routed through the same formatter so the log pipeline sees one schema.",
    ),
    (
        "Last infra thing: how should we deploy staging?",
        "Use the existing Fly.io org: `fly.toml` with one shared-cpu machine, the Docker image from CI pushed to "
        "the Fly registry on merges to main, `fly secrets` for DATABASE_URL and SECRET_KEY, and a release command "
        "that runs `flask db upgrade` before new machines take traffic. Rollback is `fly releases rollback`.",
    ),
    # 16 - DUPLICATE-FUNCTION TRAP
    (
        "Back to features. Write a helper that formats a task's due date for the email digest.",
        "(scripted reply omitted - the check is on the context the model would receive)",
    ),
    # 17 - filler
    (
        "Also the digest email should list tasks grouped by project.",
        "Grouping by `task.project.name` with `itertools.groupby` after sorting by project name works; "
        "tasks without a project go under 'Inbox'.",
    ),
    # 18 - RENAMED-API TRAP
    (
        "Now call get_user_tasks from the weekly digest job for each subscribed user.",
        "(scripted reply omitted - the check is on the context the model would receive)",
    ),
]

TRAPS: list[Trap] = [
    Trap(
        name="duplicate-function trap",
        exchange=16,
        required="def format_due_date(",
        stale=None,
        planted_at=2,
        description="a due-date formatter already exists (exchange 2); the context must surface it so it is reused, not rewritten",
    ),
    Trap(
        name="renamed-API trap",
        exchange=18,
        required="def get_user_tasks(uid",
        stale="get_user_tasks(user_id",
        planted_at=9,
        description="get_user_tasks was renamed user_id -> uid at exchange 9; the context must carry the new signature and never an unmarked old one",
    ),
]
