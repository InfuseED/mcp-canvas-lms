"""Simple profile→tool mapping."""
from __future__ import annotations

from typing import Final, List

READONLY_TOOLS: Final[List[str]] = [
    "canvas_get_account",
    "canvas_get_account_reports",
    "canvas_get_announcement",
    "canvas_get_assignment",
    "canvas_get_conversation",
    "canvas_get_course",
    "canvas_get_course_grades",
    "canvas_get_dashboard",
    "canvas_get_dashboard_cards",
    "canvas_get_discussion",
    "canvas_get_discussion_topic",
    "canvas_get_file",
    "canvas_get_module",
    "canvas_get_module_item",
    "canvas_get_page",
    "canvas_get_quiz",
    "canvas_get_rubric",
    "canvas_get_submission",
    "canvas_get_syllabus",
    "canvas_get_upcoming_assignments",
    "canvas_get_user_grades",
    "canvas_get_user_profile",
    "canvas_health_check",
    "canvas_list_account_courses",
    "canvas_list_account_users",
    "canvas_list_announcements",
    "canvas_list_assignment_groups",
    "canvas_list_assignments",
    "canvas_list_calendar_events",
    "canvas_list_conversation_messages",
    "canvas_list_conversations",
    "canvas_list_courses",
    "canvas_list_discussion_entries",
    "canvas_list_discussion_replies",
    "canvas_list_discussion_topics",
    "canvas_list_discussions",
    "canvas_list_enrollments",
    "canvas_list_files",
    "canvas_list_folders",
    "canvas_list_module_items",
    "canvas_list_modules",
    "canvas_list_notifications",
    "canvas_list_pages",
    "canvas_list_quizzes",
    "canvas_list_rubrics",
    "canvas_list_sub_accounts",
]

_BUILDER_ONLY: Final[List[str]] = [
    "canvas_add_recipients",
    "canvas_conclude_enrollment",
    "canvas_create_announcement",
    "canvas_create_assignment",
    "canvas_create_conversation",
    "canvas_create_course",
    "canvas_create_discussion",
    "canvas_create_discussion_entry",
    "canvas_create_discussion_reply",
    "canvas_create_quiz",
    "canvas_enroll_user",
    "canvas_mark_conversation_read",
    "canvas_mark_module_item_complete",
    "canvas_post_to_discussion",
    "canvas_send_conversation_message",
    "canvas_start_quiz_attempt",
    "canvas_submit_assignment",
    "canvas_submit_grade",
    "canvas_update_assignment",
    "canvas_update_course",
    "canvas_update_discussion",
    "canvas_update_user_profile",
]

BUILDER_TOOLS: Final[List[str]] = sorted({*READONLY_TOOLS, *_BUILDER_ONLY})

PROFILES: dict[str, list[str]] = {
    "readonly": READONLY_TOOLS,
    "builder": BUILDER_TOOLS,
    "admin": ["*"],
}


__all__ = ["PROFILES"]
