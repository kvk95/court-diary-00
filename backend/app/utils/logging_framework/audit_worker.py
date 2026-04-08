# app\utils\logging_framework\audit_worker.py

# app/core/audit_worker.py

from app.database.models.base.session import get_session
from app.database.repositories.login_audit_repository import LoginAuditRepository
from app.utils.logging_framework.audit_queue import audit_queue

async def audit_worker():
    while True:
        task = await audit_queue.get()

        try:
            async for session in get_session():
                repo = LoginAuditRepository()
                await repo.log_login(
                    session=session,
                    user_id=task["user_id"],
                    loginRequest=task["loginRequest"],
                    status_code=task["status_code"],
                    failure_reason=task["failure_reason"],
                    chamber_id=task["chamber_id"],
                )
        except Exception as e:
            # log error (VERY IMPORTANT)
            print(f"Audit worker error: {e}")
        finally:
            audit_queue.task_done()