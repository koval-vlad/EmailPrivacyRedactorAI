import reflex as rx
from typing import Callable, Optional


def auto_clear_page_button(
    on_clear: Callable,
    has_original_data_condition: Optional[rx.Var] = None,
    button_id: str = "auto_clear_btn",
) -> rx.Component:
    """
    Generic component for auto-clearing form on page refresh.
    
    Args:
        on_clear: Callback function to call when clearing (e.g., State.handle_new_email)
        has_original_data_condition: Optional condition to check if original data exists.
                                   If provided, form won't clear if this condition is true.
                                   Should be a boolean Var (e.g., State.original_content != "")
        button_id: ID for the hidden button (default: "auto_clear_btn")
    
    Returns:
        rx.Component with hidden button and auto-clear scripts
    """
    return rx.fragment(
        # Script to detect page refresh and set flag for clearing
        rx.script(
            """
            (function() {
                // Detect if this is a page refresh
                const navEntry = performance.getEntriesByType('navigation')[0];
                const isRefresh = navEntry && navEntry.type === 'reload';
                
                // Set flag to clear form if it's a refresh
                if (isRefresh) {
                    sessionStorage.setItem('clearFormOnLoad', 'true');
                }
            })();
            """
        ),
        # Hidden marker to indicate if we have original data (coming from preview, don't clear)
        rx.cond(
            has_original_data_condition if has_original_data_condition is not None else False,
            rx.box(data_has_original="true", style={"display": "none"}),
        ),
        # Hidden button to trigger clear on page refresh - always present
        rx.button(
            "",
            on_click=on_clear,
            id=button_id,
            style={"display": "none"},
        ),
        # Script to auto-clear on page refresh
        rx.script(
            f"""
            (function() {{
                // Wait for page to be fully loaded, then check and clear
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', clearIfNeeded);
                }} else {{
                    clearIfNeeded();
                }}
                
                function clearIfNeeded() {{
                    const shouldClear = sessionStorage.getItem('clearFormOnLoad') === 'true';
                    const hasOriginalData = document.querySelector('[data-has-original]');
                    
                    // Clear if flag is set and we don't have original data (not from preview)
                    if (shouldClear && !hasOriginalData) {{
                        sessionStorage.removeItem('clearFormOnLoad');
                        // Use multiple attempts to ensure button exists and is clickable
                        let attempts = 0;
                        const tryClear = () => {{
                            const btn = document.getElementById('{button_id}');
                            if (btn) {{
                                // Force click using multiple methods for reliability
                                btn.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true }}));
                                setTimeout(() => btn.click(), 10);
                            }} else if (attempts < 50) {{
                                attempts++;
                                setTimeout(tryClear, 50);
                            }}
                        }};
                        tryClear();
                    }}
                }}
            }})();
            """
        ),
    )

