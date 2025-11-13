# Canvas MCP Server (FastAPI)

A Python 3.11+ FastAPI implementation of the Canvas LMS Model Context Protocol (MCP) server. It exposes the full set of tools
from the original TypeScript project—courses, enrollments, assignments, submissions, modules, discussions, announcements,
conversations, quizzes, files, pages, calendar events, dashboard data, grades, notifications, syllabus access, accounts, users,
sub-accounts, and account reports—over a single MCP-compatible API surface.

## Supported tool groups
- **Health** – verify Canvas connectivity before exposing any other tooling.
- **Courses & Enrollments** – list, inspect, create, update, delete courses and enroll or conclude users.
- **Assignments & Submissions** – manage assignments, assignment groups, submissions, and grading operations.
- **Modules & Module Items** – list modules/items and mark completion states.
- **Discussions, Announcements & Conversations** – full read/write coverage for discussion topics, announcement posts, and inbox
  conversations (including replies and message threads).
- **Quizzes & Rubrics** – inspect quizzes/rubrics, create quizzes, and start quiz attempts.
- **Files, Pages & Syllabus** – list files/folders/pages and fetch syllabus bodies for courses.
- **Calendar, Dashboard & Notifications** – pull calendar events, dashboard payloads, upcoming assignments, and activity stream
  notifications.
- **Grades & Profiles** – fetch course/user grade summaries and update profile metadata.
- **Accounts, Users & Reports** – administer accounts, list account courses/users/sub-accounts, create users, and start Canvas
  account reports.

## Local development
1. Create an `.env` by copying `.env.example` and filling in at least `CANVAS_BASE_URL` and `CANVAS_API_TOKEN`.
2. Install dependencies and run the API:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e .
   uvicorn app.main:app --reload
   ```
3. Call the FastAPI endpoints:
   - `GET /healthz` – basic process health.
   - `GET /mcp/tools` – discover tools (filtered by `MCP_PROFILE` if set).
   - `POST /mcp/tools/{tool_name}` – invoke any registered tool by supplying a JSON payload.

## Developer workflow
For a faster loop you can rely on the included `Makefile` targets (or run the commands directly):

```bash
make install   # pip install -e .[dev]
make run       # uvicorn app.main:app --reload
make lint      # ruff check .
make test      # pytest
```

When iterating locally, export `MCP_PROFILE` (`readonly`, `builder`, or leave unset for admin) before starting the server so `/mcp/tools` returns the expected subset of handlers.

## Docker
```bash
docker build -t canvas-mcp .
docker run --env-file ./.env -p 8000:8000 canvas-mcp
```

## Example MCP payloads
```http
POST /mcp/tools/canvas_list_courses
{
  "payload": {
    "include_ended": false,
    "enrollment_state": "active"
  }
}

POST /mcp/tools/canvas_create_discussion
{
  "payload": {
    "course_id": 12345,
    "discussion": {
      "title": "Unit 3 Q&A",
      "message": "<p>Post your questions before the review session.</p>",
      "published": true
    }
  }
}

POST /mcp/tools/canvas_create_account_report
{
  "payload": {
    "account_id": 42,
    "report": "provisioning",
    "parameters": {
      "terms": ["term_2024"]
    }
  }
}
```

## Configuration
The server reads configuration from environment variables (or a `.env` file):

| Variable            | Description                                         | Default |
|---------------------|-----------------------------------------------------|---------|
| `CANVAS_BASE_URL`   | Canvas instance base URL (e.g., `https://foo.instructure.com`) | — |
| `CANVAS_API_TOKEN`  | Canvas API token with the required permissions      | — |
| `LOG_LEVEL`         | Python log level (`INFO`, `DEBUG`, etc.)            | `INFO`  |
| `MCP_PROFILE`       | Optional profile to limit exposed tools (`readonly`, `builder`, `admin`) | unset |

Once the service is running you can inspect every tool that is available under your profile via `GET /mcp/tools` and invoke
individual operations through `POST /mcp/tools/{tool_name}`.
