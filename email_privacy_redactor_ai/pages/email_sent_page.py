import reflex as rx
from email_privacy_redactor_ai.email_privacy_redactor_ai import EmailPrivacyRedactorAI


def email_sent_page() -> rx.Component:
    """Success screen after sending email"""
    return rx.fragment(
        rx.html(
            """
            <style>
            :root {
                color-scheme: light !important;
                forced-color-adjust: none;
            }
            * {
                forced-color-adjust: none !important;
            }
            body {
                background-color: #f0fdf4;
                color: #0f172a;
            }
            body, .rx-Text, .rx-heading, .rx-Heading, h1, h2, h3, h4, h5, h6, label, span, small {
                color: #0f172a !important;
                -webkit-text-fill-color: #0f172a !important;
            }
            button,
            .rx-Button__root,
            button *,
            .rx-Button__root * {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                background-color: #1d4ed8 !important;
                border-color: #1d4ed8 !important;
            }
            .rx-Button__root[variant="outline"],
            button[variant="outline"] {
                background-color: transparent !important;
                color: #1d4ed8 !important;
                border-color: #1d4ed8 !important;
            }
            button:disabled,
            .rx-Button__root:disabled {
                opacity: 0.6 !important;
            }
            </style>
            """
        ),
        rx.center(
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
        ),
    )

