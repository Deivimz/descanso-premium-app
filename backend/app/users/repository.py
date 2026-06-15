from app.shared.base_repository import BaseRepository
from app.users.model import User

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def find_by_email(self, email: str) -> User | None:
        return await self.model.find_one(self.model.email == email)

    async def find_by_username(self, username: str) -> User | None:
        return await self.model.find_one(self.model.username == username)

    async def find_by_rut(self, rut: str) -> User | None:
        return await self.model.find_one(self.model.rut == rut)
