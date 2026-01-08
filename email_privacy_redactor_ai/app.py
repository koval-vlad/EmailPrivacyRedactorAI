import reflex as rx
from email_privacy_redactor_ai.index_page import index_page
from dotenv import load_dotenv 
import os

load_dotenv()  # This loads .env file
app = rx.App()
app.add_page(index_page, route="/")

