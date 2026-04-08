from typing import List, Optional, Tuple, Dict

from sqlalchemy import select, func, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.email_link import EmailLink

@apply_repo_context
class EmailLinkRepository(BaseRepository[EmailLink]):
    def __init__(self):
        super().__init__(EmailLink)
