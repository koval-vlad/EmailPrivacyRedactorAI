import reflex as rx
from typing import Callable


def checkbox_input(
    label: str,
    checkbox_checked: bool = True,
    input_value: str = "",
    on_checkbox_change: Callable = None,
    on_input_change: Callable = None,
    placeholder: str = "",
    disabled: bool = False,
) -> rx.Component:
    """
    A combined checkbox + input component with checkbox INSIDE the input box
    
    Args:
        label: Label text for the checkbox
        checkbox_checked: Whether checkbox is checked
        input_value: Value of the input field
        on_checkbox_change: Callback when checkbox changes (pass State.set_field_name)
        on_input_change: Callback when input changes (pass State.set_field_name)
        placeholder: Placeholder text for input
        disabled: Whether both checkbox and input are disabled
    
    Returns:
        rx.Component with checkbox inside input box
    """
    return rx.box(
        rx.hstack(
            rx.checkbox(
                label,
                checked=checkbox_checked,
                on_change=on_checkbox_change,
                disabled=disabled,
                size="1",
                color_scheme="blue",
                style={
                    "font-size": "0.65rem",
                    "font-weight": "bold",
                    "color": "#1e3a8a",
                },
            ),
            rx.el.input(
                value=input_value,
                on_change=on_input_change,
                placeholder=placeholder,
                disabled=disabled,
                style={
                    "border": "none",
                    "outline": "none",
                    "box-shadow": "none",
                    "background": "transparent",
                    "flex": "1",
                    "padding": "0",
                    "font-size": "0.65rem",
                    "width": "100%",
                },
            ),
            spacing="1",
            align="center",
            width="100%",
        ),
        padding_x="2px",
        padding_y="2px",
        border="1px solid #d4d4d8",
        border_radius="6px",
        background="white" if not disabled else "#f4f4f5",
        width="100%",
        style={
            ":focus-within": {
                "border-color": "#3b82f6"
            } if not disabled else {},
            ":hover": {
                "border-color": "#a1a1aa" if not disabled else "#d4d4d8",
            },
            "cursor": "text" if not disabled else "not-allowed",
            "opacity": "1" if not disabled else "0.6",
        },
    )