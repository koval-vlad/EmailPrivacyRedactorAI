import reflex as rx
from email_privacy_redactor_ai.email_privacy_redactor_ai import EmailPrivacyRedactorAI


def email_preview_page() -> rx.Component:
    """Preview screen showing redacted content"""
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
                background-color: #eff6ff;
                color: #0f172a;
            }
            body, .rx-Text, .rx-heading, .rx-Heading, h1, h2, h3, h4, h5, h6, label, span, small {
                color: #0f172a !important;
                -webkit-text-fill-color: #0f172a !important;
            }
            input[type="text"],
            input[type="email"],
            input[type="url"],
            input[type="tel"],
            input[type="password"],
            textarea,
            textarea *,
            .rx-textarea,
            .rx-text-area,
            .rx-TextArea,
            .rx-TextArea__textarea,
            .rx-Textarea__textarea,
            .rx-input__field,
            .rx-text-area__field,
            .rx-TextArea,
            .rx-text-area {
                color: #0f172a !important;
                background-color: #ffffff !important;
                border: 1px solid #d1d5db !important;
                box-shadow: 0 0 0 1px #d1d5db inset !important;
                border-radius: 4px !important;
                transition: box-shadow 0.15s ease, border-color 0.15s ease;
            }
            input[type="text"]:focus-visible,
            input[type="email"]:focus-visible,
            input[type="url"]:focus-visible,
            input[type="tel"]:focus-visible,
            input[type="password"]:focus-visible,
            textarea:focus-visible,
            .rx-input__field:focus-visible,
            .rx-text-area__field:focus-visible {
                border-color: #2563eb !important;
                box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25) inset !important;
                outline: none !important;
            }
            input::placeholder,
            textarea::placeholder {
                color: #94a3b8 !important;
            }
            button,
            .rx-Button__root,
            button *,
            .rx-Button__root * {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                text-shadow: none !important;
                background-color: #1d4ed8 !important;
                border-color: #1d4ed8 !important;
            }
            .rx-Button__root[variant="outline"],
            button[variant="outline"] {
                background-color: transparent !important;
                color: #1d4ed8 !important;
                border-color: #1d4ed8 !important;
            }
            .rx-Button__root:disabled,
            button:disabled {
                opacity: 0.6 !important;
            }
            .rx-Checkbox,
            .rx-Checkbox__control,
            .rx-Checkbox__label {
                background-color: #ffffff !important;
                border: 2px solid #1d4ed8 !important;
                box-shadow: none !important;
            }
            .rx-Checkbox[data-state="unchecked"] .rx-Checkbox__control,
            .rx-Checkbox[data-state="unchecked"] .rx-Checkbox__control::before,
            .rx-Checkbox__control::before {
                background-color: #ffffff !important;
            }
            [class*="Checkbox"],
            [class*="checkbox"] {
                background-color: #ffffff !important;
                border: 2px solid #1d4ed8 !important;
                box-shadow: none !important;
                forced-color-adjust: none !important;
            }
            [class*="Checkbox__control"],
            [class*="checkbox__control"] {
                background-color: #ffffff !important;
                border-color: #1d4ed8 !important;
                box-shadow: none !important;
            }
            [class*="Checkbox__control"]::before,
            [class*="checkbox__control"]::before {
                background-color: #ffffff !important;
            }
            .rx-Checkbox__label {
                color: #1e3a8a !important;
            }
            button .rx-icon,
            .rx-button .rx-icon,
            .rx-Button__root .rx-icon {
                color: #ffffff !important;
                fill: #ffffff !important;
            }
            input[type="checkbox"] {
                background-color: #ffffff !important;
                border: 2px solid #1d4ed8 !important;
                accent-color: #1d4ed8 !important;
                box-shadow: none !important;
            }
            input[type="checkbox"]:not(:checked) {
                background-color: #ffffff !important;
            }
            </style>
            <script>
            (() => {
                const targets = () => [
                    ...new Set([
                        ...document.querySelectorAll(
                            "textarea, .rx-textarea textarea, .rx-text-area textarea, .rx-TextArea textarea, .rx-Textarea__textarea, .rx-TextArea__textarea"
                        ),
                    ]),
                };
                const applyStyles = () => {
                    targets().forEach((el) => {
                        el.style.setProperty("color", "#0f172a", "important");
                        el.style.setProperty("background-color", "#ffffff", "important");
                        el.style.setProperty("border-color", "#d1d5db", "important");
                        el.style.setProperty("-webkit-text-fill-color", "#0f172a", "important");
                        el.style.setProperty("text-shadow", "none", "important");
                    });
                };
                const observer = new MutationObserver(applyStyles);
                observer.observe(document.documentElement, { attributes: true, childList: true, subtree: true });
                document.addEventListener("DOMContentLoaded", applyStyles);
                applyStyles();
            })();
            </script>
            """
        ),
        rx.box(
            rx.container(
            rx.vstack(
                rx.hstack(
                    rx.icon("shield", size=24, color="green"),
                    rx.heading("Preview Redacted Email", size="4"),
                    spacing="2",
                    align="center",
                    justify_content="center",
                    width="100%",
                ),
                
                # Form - Full width layout (2 columns)
                rx.vstack(
                    # Top row: To, CC, Subject (left) and AI Feedback (right)
                    rx.hstack(
                        rx.vstack(
                            rx.vstack(
                                rx.text("To:", size="2", weight="bold", color="gray.700"),
                                rx.box(
                                    rx.text(EmailPrivacyRedactorAI.to_email),
                                    padding="3",
                                    bg="gray.50",
                                    border_radius="md",
                                    border="1px solid",
                                    border_color="gray.200",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="1",
                            ),
                            rx.cond(
                                EmailPrivacyRedactorAI.cc_email != "",
                                rx.vstack(
                                    rx.text("CC:", size="2", weight="bold", color="gray.700"),
                                    rx.box(
                                        rx.text(EmailPrivacyRedactorAI.cc_email),
                                        padding="3",
                                        bg="gray.50",
                                        border_radius="md",
                                        border="1px solid",
                                        border_color="gray.200",
                                        width="100%",
                                    ),
                                    width="100%",
                                    spacing="1",
                                ),
                            ),
                            rx.vstack(
                                rx.text("Subject:", size="2", weight="bold", color="gray.700"),
                                rx.box(
                                    rx.text(EmailPrivacyRedactorAI.subject),
                                    padding="3",
                                    bg="gray.50",
                                    border_radius="md",
                                    border="1px solid",
                                    border_color="gray.200",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="1",
                            ),
                            width="100%",
                            spacing="4",
                            flex="2",
                        ),
                        rx.vstack(
                            rx.text("AI Feedback:", size="2", weight="bold", color="gray.700"),
                            rx.text_area(
                                value=EmailPrivacyRedactorAI.ai_feedback,
                                placeholder="AI feedback will appear here...",
                                height="12rem",
                                width="100%",                                
                                bg="gray.50",
                                overflow_y="auto",
                                font_family="monospace",
                                font_size="0.875rem",
                                style={
                                    "color": "#0f172a !important",
                                    "-webkit-text-fill-color": "#0f172a !important",
                                },
                            ),
                            width="100%",
                            spacing="1",
                            flex="1",
                        ),
                        width="100%",
                        spacing="4",
                        align="start",
                        flex_wrap="wrap",
                    ),
                    # Bottom row: Redacted Content (left) and Original Content (right)
                    rx.hstack(
                        rx.vstack(
                            rx.text("Redacted Content (Editable):", size="2", weight="bold", color="gray.700"),
                            rx.text_area(
                                value=EmailPrivacyRedactorAI.redacted_content,
                                on_change=EmailPrivacyRedactorAI.set_redacted_content,
                                placeholder="Redacted content will appear here...",
                                height="25rem",
                                font_family="monospace",
                                width="100%",
                                resize="vertical",
                                style={
                                    "color": "#0f172a !important",
                                    "-webkit-text-fill-color": "#0f172a !important",
                                },
                            ),
                            width="100%",
                            spacing="1",
                            flex="2",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Original Content:", size="2", weight="bold", color="gray.700"),
                                rx.icon_button(
                                    rx.icon("maximize-2", size=16),
                                    on_click=EmailPrivacyRedactorAI.open_comparison_modal,
                                    variant="ghost",
                                    size="2",
                                    color_scheme="gray",
                                    cursor="pointer",
                                    title="Compare Redacted and Original Content",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.text_area(
                                value=EmailPrivacyRedactorAI.original_content,
                                placeholder="Original content will appear here...",
                                height="25rem",
                                width="100%",                                
                                bg="gray.50",
                                overflow_y="auto",
                                font_family="monospace",
                                font_size="0.875rem",
                                style={
                                    "color": "#0f172a !important",
                                    "-webkit-text-fill-color": "#0f172a !important",
                                },
                            ),
                            width="100%",
                            spacing="1",
                            flex="1",
                        ),
                        width="100%",
                        spacing="4",
                        align="start",
                        flex_wrap="wrap",
                    ),
                    
                    # Redacted images
                    rx.cond(
                        EmailPrivacyRedactorAI.redacted_images.length() > 0,
                        rx.vstack(
                            rx.text("Redacted Images:", size="2", weight="bold", color="gray.700"),
                            rx.grid(
                                rx.foreach(
                                    EmailPrivacyRedactorAI.redacted_images,
                                    lambda img, idx: rx.box(
                                        rx.image(
                                            src=f"data:image/png;base64,{img}",
                                            max_width="150px",
                                            width="100%",
                                            height="auto",
                                            border_radius="md",
                                            border="1px solid",
                                            border_color="gray.200",
                                            cursor="pointer",
                                            on_click=EmailPrivacyRedactorAI.open_image_modal(idx),
                                        ),
                                    ),
                                ),
                                columns="4",
                                spacing="2",
                                width="100%",
                            ),
                            width="100%",
                            spacing="2",
                        ),
                    ),
                    
                    width="100%",
                    spacing="4",
                ),
                
                # Action buttons
                rx.hstack(
                    rx.button(
                        rx.icon("arrow-left", size=16),
                        "Back",
                        on_click=EmailPrivacyRedactorAI.handle_back,
                        variant="outline",
                        size="3",
                        cursor="pointer",
                        width="auto",
                    ),
                    rx.button(
                        rx.icon("send", size=16),
                        "Send Email",
                        on_click=EmailPrivacyRedactorAI.send_email,
                        size="3",
                        flex="1",
                        cursor="pointer",
                    ),
                    width="100%",
                    spacing="3",
                    flex_wrap="wrap",
                ),
                
                spacing="6",
                width="100%",
            ),
            max_width="80%",
            width="80%",
            padding="6",
            bg="white",
            border_radius="lg",
            box_shadow="xl",
            center_content=True,
        ),
        min_height="100vh",
        bg="linear-gradient(to bottom right, #eff6ff, #e0e7ff)",
        padding="4",
        display="flex",
        justify_content="center",
        align_items="flex-start",
        width="100%",
        style={"color-scheme": "light"},
        ),
        # Image modal overlay - shows redacted and original images side by side
        rx.cond(
            EmailPrivacyRedactorAI.selected_image_index >= 0,
            rx.box(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.spacer(),
                            rx.icon_button(
                                rx.icon("x", size=20),
                                on_click=EmailPrivacyRedactorAI.close_image_modal,
                                variant="soft",
                                color_scheme="gray",
                                size="3",
                                cursor="pointer",
                            ),
                            width="100%",
                            align="end",
                        ),
                        rx.hstack(
                            rx.vstack(
                                rx.text(
                                    "Redacted Image",
                                    size="3",
                                    weight="bold",
                                    color="gray.700",
                                    text_align="center",
                                    width="100%",
                                ),
                                rx.center(
                                rx.image(
                                    src=f"data:image/png;base64,{EmailPrivacyRedactorAI.selected_image}",
                                    max_width="55vw",
                                    max_height="90vh",
                                    object_fit="contain",
                                    border_radius="md",
                                    border="2px solid",
                                    border_color="green.300",
                                    bg="white",
                                ),
                                    width="100%",
                                ),
                                spacing="2",
                                width="100%",
                                flex="1",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Original Image",
                                    size="3",
                                    weight="bold",
                                    color="gray.700",
                                    text_align="center",
                                    width="100%",
                                ),
                                rx.center(
                                    rx.cond(
                                        EmailPrivacyRedactorAI.selected_image_index < EmailPrivacyRedactorAI.uploaded_images.length(),
                                        rx.image(
                                            src=f"data:image/png;base64,{EmailPrivacyRedactorAI.uploaded_images[EmailPrivacyRedactorAI.selected_image_index]}",
                                            max_width="55vw",
                                            max_height="90vh",
                                            object_fit="contain",
                                            border_radius="md",
                                            border="2px solid",
                                            border_color="blue.300",
                                            bg="white",
                                        ),
                                        rx.text(
                                            "Original image not available",
                                            color="gray.500",
                                            size="2",
                                        ),
                                    ),
                                    width="100%",
                                ),
                                spacing="2",
                                width="100%",
                                flex="1",
                            ),
                            width="100%",
                            spacing="6",
                            align="start",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    width="98vw",
                    max_width="1600px",
                    max_height="95vh",
                    padding="6",
                    bg="white",
                    border_radius="lg",
                    box_shadow="2xl",
                    overflow_y="auto",
                ),
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0, 0, 0, 0.75)",
                display="flex",
                align_items="center",
                justify_content="center",
                z_index=1000,
            ),
        ),
        # Content Comparison Modal - shows Redacted and Original side by side
        rx.cond(
            EmailPrivacyRedactorAI.show_comparison_modal,
            rx.box(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Compare Content", size="5", color="gray.800"),
                            rx.spacer(),
                            rx.icon_button(
                                rx.icon("x", size=20),
                                on_click=EmailPrivacyRedactorAI.close_comparison_modal,
                                variant="soft",
                                color_scheme="gray",
                                size="3",
                                cursor="pointer",
                            ),
                            width="100%",
                            align="center",
                        ),
                        rx.hstack(
                            rx.vstack(
                                rx.text(
                                    "Redacted Content",
                                    size="3",
                                    weight="bold",
                                    color="green.700",
                                    text_align="center",
                                    width="100%",
                                ),
                                rx.text_area(
                                    value=EmailPrivacyRedactorAI.redacted_content,
                                    on_change=EmailPrivacyRedactorAI.set_redacted_content,
                                    placeholder="Redacted content...",
                                    height="70vh",
                                    width="100%",
                                    font_family="monospace",
                                    resize="vertical",
                                    border="2px solid",
                                    border_color="green.300",
                                ),
                                width="100%",
                                spacing="2",
                                flex="1",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Original Content",
                                    size="3",
                                    weight="bold",
                                    color="blue.700",
                                    text_align="center",
                                    width="100%",
                                ),
                                rx.text_area(
                                    value=EmailPrivacyRedactorAI.original_content,
                                    placeholder="Original content...",
                                    height="70vh",
                                    width="100%",                                    
                                    bg="gray.50",
                                    overflow_y="auto",
                                    font_family="monospace",
                                    border="2px solid",
                                    border_color="blue.300",
                                ),
                                width="100%",
                                spacing="2",
                                flex="1",
                            ),
                            width="100%",
                            spacing="4",
                            align="start",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    width="95vw",
                    max_width="1600px",
                    max_height="90vh",
                    padding="6",
                    bg="white",
                    border_radius="lg",
                    box_shadow="2xl",
                    overflow_y="auto",
                ),
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0, 0, 0, 0.75)",
                display="flex",
                align_items="center",
                justify_content="center",
                z_index=1000,
            ),
        ),
    )

