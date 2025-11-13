"""Helpers for registering MCP tool groups."""
from __future__ import annotations

from app.mcp.server import MCPServer
from app.mcp.tools.accounts import register_account_tools
from app.mcp.tools.announcements import register_announcement_tools
from app.mcp.tools.assignments import register_assignment_tools
from app.mcp.tools.calendar import register_calendar_tools
from app.mcp.tools.conversations import register_conversation_tools
from app.mcp.tools.courses import register_course_tools
from app.mcp.tools.dashboard import register_dashboard_tools
from app.mcp.tools.discussions import register_discussion_tools
from app.mcp.tools.enrollments import register_enrollment_tools
from app.mcp.tools.files import register_file_tools
from app.mcp.tools.grades import register_grade_tools
from app.mcp.tools.health import register_health_tool
from app.mcp.tools.modules import register_module_tools
from app.mcp.tools.notifications import register_notification_tools
from app.mcp.tools.pages import register_page_tools
from app.mcp.tools.quizzes import register_quiz_tools
from app.mcp.tools.reports import register_report_tools
from app.mcp.tools.rubrics import register_rubric_tools
from app.mcp.tools.submissions import register_submission_tools
from app.mcp.tools.syllabus import register_syllabus_tools
from app.mcp.tools.users import register_user_tools


def register_all_tools(server: MCPServer) -> None:
    """Register every tool group with the provided server."""

    register_health_tool(server)
    register_course_tools(server)
    register_enrollment_tools(server)
    register_assignment_tools(server)
    register_submission_tools(server)
    register_module_tools(server)
    register_discussion_tools(server)
    register_announcement_tools(server)
    register_conversation_tools(server)
    register_file_tools(server)
    register_page_tools(server)
    register_calendar_tools(server)
    register_dashboard_tools(server)
    register_grade_tools(server)
    register_user_tools(server)
    register_quiz_tools(server)
    register_rubric_tools(server)
    register_notification_tools(server)
    register_syllabus_tools(server)
    register_account_tools(server)
    register_report_tools(server)


__all__ = ["register_all_tools"]
