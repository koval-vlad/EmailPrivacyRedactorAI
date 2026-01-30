import reflex as rx

config = rx.Config(
    app_name="email_privacy_redactor_ai",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    # Windows: bind backend to 127.0.0.1 so frontend can reach it; use explicit ports
    backend_host="127.0.0.1",
    frontend_port=3000,
    backend_port=8000,
    api_url="http://127.0.0.1:8000",
    deploy_url="http://localhost:3000",
)
