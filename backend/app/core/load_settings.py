# app/core/load_settings.py

from app.core.runtime_settings import set_runtime_settings
from app.database.repositories.global_settings_repository import GlobalSettingsRepository
from app.utils.utilities import decode_text


async def load_global_settings(session):
    repo = GlobalSettingsRepository()
    row = await repo.get_first(session)

    if not row:
        return
    
    smtp_settings = {
        "SMTP_SERVER": row.smtp_host,
        "SMTP_SERVER_PORT": row.smtp_port,
        "SMTP_SERVER_USERNAME": decode_text(row.smtp_user_name) if row.smtp_user_name else None,
        "SMTP_SERVER_PASSWORD": decode_text(row.smtp_password) if row.smtp_password else None,
        "SMTP_USE_TLS": row.smtp_use_tls,
    }

    print("*******************************")
    print(smtp_settings)
    print("*******************************")

    set_runtime_settings(smtp_settings)