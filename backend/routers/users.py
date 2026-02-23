from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models.user import User
from utils import api_response

router = APIRouter(prefix="/huajian", tags=["用户"])


@router.get("/integral/user/{email}")
def get_user_info(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return api_response(data=None, status=404, message="用户不存在")
    return api_response(data=user.to_user_info())


@router.put("/users/updateAvatar")
def update_avatar(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    avatar = data.get("avatar", "")
    user.avatar = avatar
    db.commit()
    return api_response(data=user.to_user_info())


@router.put("/users/updatePersonInfo")
def update_person_info(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if "name" in data:
        user.name = data["name"]
    if "avatar" in data:
        user.avatar = data["avatar"]
    db.commit()
    return api_response(data=user.to_user_info())
