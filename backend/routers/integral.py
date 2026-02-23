from fastapi import APIRouter, Depends

from deps import get_current_user
from models.user import User
from utils import api_response

router = APIRouter(prefix="/huajian", tags=["本地状态"])


@router.get("/integral/getUserIntegralTotal")
def get_user_integral_total(user: User = Depends(get_current_user)):
    # 兼容历史字段，保证编辑/导出流程不被余额判断阻断。
    return api_response(data={
        "integralTotal": 99999999,
        "isattendance": True,
    })
