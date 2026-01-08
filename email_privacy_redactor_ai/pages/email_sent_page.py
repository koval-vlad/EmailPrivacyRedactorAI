import reflex as rx
from email_privacy_redactor_ai.email_privacy_redactor_ai import EmailPrivacyRedactorAI


def email_sent_page() -> rx.Component:
    """Success screen after sending email"""
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon("mail", size=32, color="green"),
                width="4rem",
                height="4rem",
                bg="green.100",
                border_radius="full",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.heading("Email Sent Successfully!", size="7"),
            rx.text("Your AI-redacted email was successfully sent.", color="gray.600"),
            rx.button(
                "Compose New Email",
                on_click=EmailPrivacyRedactorAI.handle_new_email,
                size="3",
                cursor="pointer",
            ),
            spacing="4",
            align="center",
        ),
        min_height="100vh",
        bg="linear-gradient(to bottom right, #f0fdf4, #d1fae5)",
        padding="4",
    )

