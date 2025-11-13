"""Async Canvas API client built on top of httpx."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from app.canvas.exceptions import CanvasAPIError
from app.config import Settings


class CanvasClient:
    """Async Canvas client that mirrors the TypeScript implementation."""

    def __init__(
        self,
        settings: Settings,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ) -> None:
        base = settings.canvas_base_url.rstrip("/")
        if not base.endswith("/api/v1"):
            base = f"{base}/api/v1"
        self._settings = settings
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff
        self._client: Optional[httpx.AsyncClient] = None
        self._base_url = base

    async def start(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def stop(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "CanvasClient":
        await self.start()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.stop()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------
    async def health_check(self) -> dict[str, Any]:
        """Call a lightweight Canvas endpoint to confirm connectivity."""

        return await self._request("GET", "/accounts/self")

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------
    async def list_courses(self, include_ended: bool = False, **params: Any) -> List[dict[str, Any]]:
        query: dict[str, Any] = {
            "include[]": [
                "total_students",
                "teachers",
                "term",
                "course_progress",
                "sections",
            ],
            "per_page": 100,
        }
        if not include_ended:
            query["state[]"] = ["available", "completed"]
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", "/courses", params=query)

    async def get_course(self, course_id: int) -> dict[str, Any]:
        params = {
            "include[]": [
                "total_students",
                "teachers",
                "term",
                "course_progress",
                "sections",
                "syllabus_body",
            ]
        }
        return await self._request("GET", f"/courses/{course_id}", params=params)

    async def create_course(self, account_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        body = {"course": payload}
        return await self._request("POST", f"/accounts/{account_id}/courses", json=body)

    async def update_course(self, course_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        body = {"course": payload}
        return await self._request("PUT", f"/courses/{course_id}", json=body)

    async def delete_course(self, course_id: int) -> dict[str, Any] | None:
        response = await self._request("DELETE", f"/courses/{course_id}")
        return response if isinstance(response, dict) else None

    # ------------------------------------------------------------------
    # Enrollments
    # ------------------------------------------------------------------
    async def list_enrollments(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/enrollments", params=query)

    async def enroll_user(self, course_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        body = {"enrollment": payload}
        return await self._request("POST", f"/courses/{course_id}/enrollments", json=body)

    async def conclude_enrollment(self, course_id: int, enrollment_id: int) -> dict[str, Any] | None:
        response = await self._request("DELETE", f"/courses/{course_id}/enrollments/{enrollment_id}")
        return response if isinstance(response, dict) else None

    # ------------------------------------------------------------------
    # Assignments
    # ------------------------------------------------------------------
    async def list_assignments(
        self,
        course_id: int,
        *,
        include_submissions: bool = False,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query: dict[str, Any] = {
            "include[]": ["assignment_group", "rubric", "due_at"],
            "per_page": 100,
        }
        if include_submissions:
            query["include[]"].append("submission")
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/assignments", params=query)

    async def get_assignment(
        self,
        course_id: int,
        assignment_id: int,
        *,
        include_submission: bool = False,
        **params: Any,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "include[]": ["assignment_group", "rubric"],
        }
        if include_submission:
            query["include[]"].append("submission")
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._request(
            "GET",
            f"/courses/{course_id}/assignments/{assignment_id}",
            params=query,
        )

    async def create_assignment(self, course_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        body = {"assignment": payload}
        return await self._request("POST", f"/courses/{course_id}/assignments", json=body)

    async def update_assignment(
        self,
        course_id: int,
        assignment_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"assignment": payload}
        return await self._request(
            "PUT",
            f"/courses/{course_id}/assignments/{assignment_id}",
            json=body,
        )

    async def delete_assignment(
        self,
        course_id: int,
        assignment_id: int,
    ) -> dict[str, Any] | None:
        response = await self._request(
            "DELETE",
            f"/courses/{course_id}/assignments/{assignment_id}",
        )
        return response if isinstance(response, dict) else None

    async def list_assignment_groups(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"include[]": ["assignments"]}
        query.update({k: v for k, v in params.items() if v is not None})
        data = await self._request("GET", f"/courses/{course_id}/assignment_groups", params=query)
        if isinstance(data, list):
            return data
        raise CanvasAPIError("Unexpected response format for assignment groups", 0, data)

    # ------------------------------------------------------------------
    # Submissions
    # ------------------------------------------------------------------
    async def list_submissions(
        self,
        course_id: int,
        assignment_id: int,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query: dict[str, Any] = {
            "include[]": ["submission_comments", "rubric_assessment", "assignment"],
            "per_page": 100,
        }
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate(
            "GET",
            f"/courses/{course_id}/assignments/{assignment_id}/submissions",
            params=query,
        )

    async def get_submission(
        self,
        course_id: int,
        assignment_id: int,
        user_id: int | str = "self",
        **params: Any,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "include[]": ["submission_comments", "rubric_assessment", "assignment"],
        }
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._request(
            "GET",
            f"/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}",
            params=query,
        )

    async def grade_submission(
        self,
        course_id: int,
        assignment_id: int,
        user_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"submission": payload}
        return await self._request(
            "PUT",
            f"/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}",
            json=body,
        )

    async def submit_assignment(
        self,
        course_id: int,
        assignment_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"submission": payload}
        return await self._request(
            "POST",
            f"/courses/{course_id}/assignments/{assignment_id}/submissions",
            json=body,
        )

    # ------------------------------------------------------------------
    # Files and folders
    # ------------------------------------------------------------------
    async def list_files(
        self,
        course_id: int,
        *,
        folder_id: int | None = None,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        path = f"/folders/{folder_id}/files" if folder_id else f"/courses/{course_id}/files"
        return await self._paginate("GET", path, params=query)

    async def get_file(self, file_id: int, **params: Any) -> dict[str, Any]:
        query = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", f"/files/{file_id}", params=query)

    async def list_folders(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/folders", params=query)

    # ------------------------------------------------------------------
    # Pages
    # ------------------------------------------------------------------
    async def list_pages(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/pages", params=query)

    async def get_page(self, course_id: int, page_url: str, **params: Any) -> dict[str, Any]:
        query = {k: v for k, v in params.items() if v is not None}
        encoded = quote(page_url, safe="")
        return await self._request("GET", f"/courses/{course_id}/pages/{encoded}", params=query)

    # ------------------------------------------------------------------
    # Calendar and upcoming events
    # ------------------------------------------------------------------
    async def list_calendar_events(self, **params: Any) -> List[dict[str, Any]]:
        query: dict[str, Any] = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        query.setdefault("type", "event")
        return await self._paginate("GET", "/calendar_events", params=query)

    async def get_upcoming_assignments(
        self,
        limit: int = 10,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query: dict[str, Any] = {"limit": limit}
        query.update({k: v for k, v in params.items() if v is not None})
        events = await self._request("GET", "/users/self/upcoming_events", params=query)
        if isinstance(events, list):
            return [event for event in events if event.get("assignment")]
        raise CanvasAPIError("Unexpected response from upcoming events", 0, events)

    # ------------------------------------------------------------------
    # Dashboard and grades
    # ------------------------------------------------------------------
    async def get_dashboard(self, **params: Any) -> dict[str, Any]:
        query = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", "/users/self/dashboard", params=query)

    async def get_dashboard_cards(self, **params: Any) -> list[dict[str, Any]]:
        query = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", "/dashboard/dashboard_cards", params=query)
        if isinstance(data, list):
            return data
        raise CanvasAPIError("Unexpected response for dashboard cards", 0, data)

    async def get_course_grades(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query: dict[str, Any] = {"include[]": ["grades", "observed_users"]}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/enrollments", params=query)

    async def get_user_grades(self, **params: Any) -> list[dict[str, Any]]:
        query = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", "/users/self/grades", params=query)
        if isinstance(data, list):
            return data
        raise CanvasAPIError("Unexpected response for user grades", 0, data)

    # ------------------------------------------------------------------
    # User profile
    # ------------------------------------------------------------------
    async def get_user_profile(self) -> dict[str, Any]:
        return await self._request("GET", "/users/self/profile")

    async def update_user_profile(self, profile_data: dict[str, Any]) -> dict[str, Any]:
        body = {"user": profile_data}
        return await self._request("PUT", "/users/self", json=body)

    # ------------------------------------------------------------------
    # Modules
    # ------------------------------------------------------------------
    async def list_modules(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"include[]": ["items"], "per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/modules", params=query)

    async def get_module(self, course_id: int, module_id: int, **params: Any) -> dict[str, Any]:
        query = {"include[]": ["items"]}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._request("GET", f"/courses/{course_id}/modules/{module_id}", params=query)

    async def list_module_items(
        self,
        course_id: int,
        module_id: int,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query = {"include[]": ["content_details"], "per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate(
            "GET",
            f"/courses/{course_id}/modules/{module_id}/items",
            params=query,
        )

    async def get_module_item(
        self,
        course_id: int,
        module_id: int,
        item_id: int,
        **params: Any,
    ) -> dict[str, Any]:
        query = {"include[]": ["content_details"]}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._request(
            "GET",
            f"/courses/{course_id}/modules/{module_id}/items/{item_id}",
            params=query,
        )

    async def mark_module_item_complete(
        self,
        course_id: int,
        module_id: int,
        item_id: int,
    ) -> dict[str, Any]:
        return await self._request(
            "PUT",
            f"/courses/{course_id}/modules/{module_id}/items/{item_id}/done",
        )

    # ------------------------------------------------------------------
    # Discussions
    # ------------------------------------------------------------------
    async def list_discussions(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"include[]": ["assignment"], "per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/discussion_topics", params=query)

    async def get_discussion(self, course_id: int, topic_id: int, **params: Any) -> dict[str, Any]:
        query = {"include[]": ["assignment"]}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._request(
            "GET",
            f"/courses/{course_id}/discussion_topics/{topic_id}",
            params=query,
        )

    async def create_discussion(self, course_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/courses/{course_id}/discussion_topics",
            json=payload,
        )

    async def update_discussion(
        self,
        course_id: int,
        topic_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return await self._request(
            "PUT",
            f"/courses/{course_id}/discussion_topics/{topic_id}",
            json=payload,
        )

    async def delete_discussion(
        self,
        course_id: int,
        topic_id: int,
    ) -> dict[str, Any] | None:
        response = await self._request(
            "DELETE",
            f"/courses/{course_id}/discussion_topics/{topic_id}",
        )
        return response if isinstance(response, dict) else None

    async def list_discussion_entries(
        self,
        course_id: int,
        topic_id: int,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate(
            "GET",
            f"/courses/{course_id}/discussion_topics/{topic_id}/entries",
            params=query,
        )

    async def create_discussion_entry(
        self,
        course_id: int,
        topic_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/courses/{course_id}/discussion_topics/{topic_id}/entries",
            json=payload,
        )

    async def list_discussion_replies(
        self,
        course_id: int,
        topic_id: int,
        entry_id: int,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate(
            "GET",
            f"/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/replies",
            params=query,
        )

    async def create_discussion_reply(
        self,
        course_id: int,
        topic_id: int,
        entry_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/replies",
            json=payload,
        )

    # ------------------------------------------------------------------
    # Announcements
    # ------------------------------------------------------------------
    async def list_announcements(
        self,
        context_codes: List[str],
        **params: Any,
    ) -> List[dict[str, Any]]:
        if not context_codes:
            raise ValueError("At least one context code is required to list announcements")
        query: dict[str, Any] = {"context_codes[]": context_codes, "per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", "/announcements", params=query)

    async def get_announcement(
        self,
        course_id: int,
        topic_id: int,
        **params: Any,
    ) -> dict[str, Any]:
        query = {"include[]": ["assignment"]}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._request(
            "GET",
            f"/courses/{course_id}/discussion_topics/{topic_id}",
            params=query,
        )

    async def create_announcement(self, course_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        announcement_payload = dict(payload)
        announcement_payload.setdefault("is_announcement", True)
        return await self._request(
            "POST",
            f"/courses/{course_id}/discussion_topics",
            json=announcement_payload,
        )

    # ------------------------------------------------------------------
    # Quizzes
    # ------------------------------------------------------------------
    async def list_quizzes(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/courses/{course_id}/quizzes", params=query)

    async def get_quiz(self, course_id: int, quiz_id: int, **params: Any) -> dict[str, Any]:
        query = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", f"/courses/{course_id}/quizzes/{quiz_id}", params=query)

    async def create_quiz(self, course_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        body = {"quiz": payload}
        return await self._request("POST", f"/courses/{course_id}/quizzes", json=body)

    async def update_quiz(
        self,
        course_id: int,
        quiz_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"quiz": payload}
        return await self._request("PUT", f"/courses/{course_id}/quizzes/{quiz_id}", json=body)

    async def delete_quiz(self, course_id: int, quiz_id: int) -> dict[str, Any] | None:
        response = await self._request("DELETE", f"/courses/{course_id}/quizzes/{quiz_id}")
        return response if isinstance(response, dict) else None

    async def start_quiz_attempt(self, course_id: int, quiz_id: int) -> dict[str, Any]:
        return await self._request("POST", f"/courses/{course_id}/quizzes/{quiz_id}/submissions")

    async def submit_quiz_attempt(
        self,
        course_id: int,
        quiz_id: int,
        submission_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"quiz_submissions": [payload]}
        return await self._request(
            "POST",
            f"/courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}/complete",
            json=body,
        )

    # ------------------------------------------------------------------
    # Rubrics
    # ------------------------------------------------------------------
    async def list_rubrics(self, course_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {k: v for k, v in params.items() if v is not None}
        return await self._paginate("GET", f"/courses/{course_id}/rubrics", params=query)

    async def get_rubric(self, course_id: int, rubric_id: int, **params: Any) -> dict[str, Any]:
        query = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", f"/courses/{course_id}/rubrics/{rubric_id}", params=query)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    async def list_notifications(self, **params: Any) -> List[dict[str, Any]]:
        query = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", "/users/self/activity_stream", params=query)
        if isinstance(data, list):
            return data
        raise CanvasAPIError("Unexpected response for notifications", 0, data)

    # ------------------------------------------------------------------
    # Syllabus
    # ------------------------------------------------------------------
    async def get_syllabus(self, course_id: int) -> dict[str, Any]:
        params = {"include[]": ["syllabus_body"]}
        course = await self._request("GET", f"/courses/{course_id}", params=params)
        return {
            "course_id": course_id,
            "syllabus_body": course.get("syllabus_body"),
        }

    # ------------------------------------------------------------------
    # Accounts and users
    # ------------------------------------------------------------------
    async def get_account(self, account_id: int, **params: Any) -> dict[str, Any]:
        query = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", f"/accounts/{account_id}", params=query)

    async def list_account_courses(self, account_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/accounts/{account_id}/courses", params=query)

    async def list_account_users(self, account_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/accounts/{account_id}/users", params=query)

    async def create_user(self, account_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", f"/accounts/{account_id}/users", json=payload)

    async def list_sub_accounts(self, account_id: int, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", f"/accounts/{account_id}/sub_accounts", params=query)

    # ------------------------------------------------------------------
    # Account reports
    # ------------------------------------------------------------------
    async def list_account_reports(self, account_id: int) -> List[dict[str, Any]]:
        data = await self._request("GET", f"/accounts/{account_id}/reports")
        if isinstance(data, list):
            return data
        raise CanvasAPIError("Unexpected response for account reports", 0, data)

    async def create_account_report(
        self,
        account_id: int,
        report: str,
        parameters: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        body = {"parameters": parameters or {}}
        return await self._request(
            "POST",
            f"/accounts/{account_id}/reports/{report}",
            json=body,
        )

    async def get_account_report(
        self,
        account_id: int,
        report: str,
        report_id: int,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/accounts/{account_id}/reports/{report}/{report_id}",
        )

    # ------------------------------------------------------------------
    # Conversations
    # ------------------------------------------------------------------
    async def list_conversations(self, **params: Any) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate("GET", "/conversations", params=query)

    async def get_conversation(self, conversation_id: int, **params: Any) -> dict[str, Any]:
        query = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", f"/conversations/{conversation_id}", params=query)

    async def list_conversation_messages(
        self,
        conversation_id: int,
        **params: Any,
    ) -> List[dict[str, Any]]:
        query = {"per_page": 100}
        query.update({k: v for k, v in params.items() if v is not None})
        return await self._paginate(
            "GET",
            f"/conversations/{conversation_id}/messages",
            params=query,
        )

    async def create_conversation(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/conversations", json=payload)

    async def send_conversation_message(
        self,
        conversation_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/conversations/{conversation_id}/add_message",
            json=payload,
        )

    async def add_conversation_recipients(
        self,
        conversation_id: int,
        recipients: List[int | str],
    ) -> dict[str, Any]:
        body = {"recipients": recipients}
        return await self._request(
            "POST",
            f"/conversations/{conversation_id}/add_recipients",
            json=body,
        )

    async def mark_conversation_read(self, conversation_id: int) -> dict[str, Any]:
        body = {"conversation": {"workflow_state": "read"}}
        return await self._request("PUT", f"/conversations/{conversation_id}", json=body)

    async def delete_conversation(self, conversation_id: int) -> dict[str, Any] | None:
        response = await self._request("DELETE", f"/conversations/{conversation_id}")
        return response if isinstance(response, dict) else None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("CanvasClient has not been started")
        return self._client

    def _auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.canvas_api_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[Any]:
        response = await self._send_request(method, path, params=params, json=json)
        return self._decode_response(response)

    async def _paginate(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
    ) -> List[dict[str, Any]]:
        results: List[dict[str, Any]] = []
        next_url: Optional[str] = path
        next_params = dict(params or {})
        while next_url:
            response = await self._send_request(method, next_url, params=next_params)
            data = self._decode_response(response)
            if isinstance(data, list):
                results.extend(data)
            else:
                raise CanvasAPIError(
                    "Unexpected response format for pagination",
                    response.status_code,
                    data,
                )
            next_url = self._parse_next_link(response.headers.get("link"))
            next_params = None
        return results

    async def _send_request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        client = await self._ensure_client()
        attempt = 0
        while True:
            try:
                response = await client.request(
                    method,
                    path,
                    headers=self._auth_headers(),
                    params=params,
                    json=json,
                )
            except httpx.HTTPError as exc:  # pragma: no cover - network failure
                if attempt >= self._max_retries:
                    raise CanvasAPIError(str(exc), 0, None) from exc
                await asyncio.sleep(self._retry_backoff * (2**attempt))
                attempt += 1
                continue

            if response.status_code >= 400:
                if response.status_code in {429} or response.status_code >= 500:
                    if attempt < self._max_retries:
                        await asyncio.sleep(self._retry_backoff * (2**attempt))
                        attempt += 1
                        continue
                raise self._error_from_response(response)

            return response

    def _decode_response(self, response: httpx.Response) -> dict[str, Any] | list[Any]:
        if response.status_code == 204:
            return {}
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            return response.json()
        return {"raw": response.text}

    def _error_from_response(self, response: httpx.Response) -> CanvasAPIError:
        try:
            payload = response.json()
        except ValueError:
            payload = response.text or None
        if isinstance(payload, dict):
            if "message" in payload:
                message = str(payload["message"])
            elif "errors" in payload and isinstance(payload["errors"], list):
                message = ", ".join(str(err.get("message", err)) for err in payload["errors"])  # type: ignore[arg-type]
            else:
                message = str(payload)
        else:
            message = str(payload)
        return CanvasAPIError(
            f"Canvas API Error ({response.status_code}): {message}",
            response.status_code,
            payload,
        )

    def _parse_next_link(self, link_header: Optional[str]) -> Optional[str]:
        if not link_header:
            return None
        for part in link_header.split(","):
            section = part.strip()
            if 'rel="next"' in section:
                start = section.find("<")
                end = section.find(">", start + 1)
                if start != -1 and end != -1:
                    return section[start + 1 : end]
        return None


__all__ = ["CanvasClient"]
