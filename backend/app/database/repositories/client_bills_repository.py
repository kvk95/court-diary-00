from typing import List, Optional, Tuple, Dict

from sqlalchemy import select, func, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.client_bills import ClientBills

@apply_repo_context
class ClientBillsRepository(BaseRepository[ClientBills]):
    def __init__(self):
        super().__init__(ClientBills)
