from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from app.users.schemas import UserCreate, UserUpdate, UserResponse
from app.users.repository import UserRepository
from app.users.model import User
from app.core.security import get_password_hash
from app.core.dependencies import require_admin
from typing import List

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, current_user: User = Depends(require_admin)):
    repo = UserRepository()
    
    if await repo.find_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    if await repo.find_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    if await repo.find_by_rut(user_in.rut):
        raise HTTPException(status_code=400, detail="El RUT ya está registrado")
        
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        rut=user_in.rut,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=user_in.is_active
    )
    created_user = await repo.create(new_user)
    return created_user

@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0, limit: int = 100, current_user: User = Depends(require_admin)
):
    repo = UserRepository()
    users = await repo.find_all(skip=skip, limit=limit)
    return users

@router.get("/{id}", response_model=UserResponse)
async def get_user(id: PydanticObjectId, current_user: User = Depends(require_admin)):
    repo = UserRepository()
    user = await repo.find_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{id}", response_model=UserResponse)
async def update_user(
    id: PydanticObjectId, user_in: UserUpdate, current_user: User = Depends(require_admin)
):
    repo = UserRepository()
    user = await repo.find_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    updated_user = await repo.update(user, update_data)
    return updated_user

@router.delete("/{id}")
async def delete_user(id: PydanticObjectId, current_user: User = Depends(require_admin)):
    repo = UserRepository()
    user = await repo.find_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Protect from deleting oneself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete current user")
        
    await repo.hard_delete(user)
    return {"message": "User deleted successfully"}
