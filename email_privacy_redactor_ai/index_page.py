import reflex as rx
from email_privacy_redactor_ai.email_privacy_redactor_ai import EmailPrivacyRedactorAI
from email_privacy_redactor_ai.pages.email_sent_page import email_sent_page
from email_privacy_redactor_ai.pages.email_preview_page import email_preview_page
from email_privacy_redactor_ai.pages.email_compose_page import email_compose_page


def index_page() -> rx.Component:
    """Main app component with conditional rendering"""
    return rx.cond(
        EmailPrivacyRedactorAI.step == "sent",
        email_sent_page(),
        rx.cond(
            EmailPrivacyRedactorAI.step == "preview",
            email_preview_page(),
            email_compose_page(),
        ),
    )

