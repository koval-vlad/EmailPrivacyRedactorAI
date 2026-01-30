import os
import warnings

import reflex as rx
from email_privacy_redactor_ai.index_page import index_page
from dotenv import load_dotenv

# Load .env; utf-8-sig strips BOM; suppress parse warnings from invalid lines
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    load_dotenv(encoding="utf-8-sig")
app = rx.App()
app.add_page(index_page, route="/")

