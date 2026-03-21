from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.user_invitations import UserInvitations

@apply_repo_context
class UserInvitationsRepository(BaseRepository[UserInvitations]):
    def __init__(self):
        super().__init__(UserInvitations)
