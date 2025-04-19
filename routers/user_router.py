from fastapi import APIRouter,HTTPException
from utils.db_rw import UserManager
from pydantic import BaseModel
import bcrypt
import re
import base64

router = APIRouter()
user_manager = UserManager()

class User(BaseModel):
    name: str
    password: str
    email: str

@router.post("/register")
async def register(user: User):
    user_dict = user.dict()
    db_user = user_manager.get_user_by_email(email=user_dict['email'])
    if db_user:
        raise HTTPException(status_code=400,detail="邮箱已被注册")
    user_dict['password'] = bcrypt.hashpw(user_dict['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # 允许更多字符，但仍然禁止一些特殊字符如 <>/\等
    if not re.match("^[^<>/\\\\|?*\"]+$", user_dict['name']):
        raise HTTPException(status_code=400, detail="用户名包含非法字符")
    try:
        user_manager.create_user(user_dict['name'],user_dict['password'],user_dict['email'])
        return {"access_token": base64.encodebytes(user_dict['name'].encode('utf-8'))}
    except Exception as e:
        raise HTTPException(status_code=500, detail="注册失败:"+str(e))

@router.post("/login")
async def login(user: User):
    user_dict = user.dict()
    # 判断是否使用邮箱登录
    if user_dict['email']:
        db_user = user_manager.get_user_by_email(email=user_dict['email'])
    # 判断是否使用用户名登录
    elif user_dict['name']:
        db_user = user_manager.get_user_by_name(name=user_dict['name'])
    if not db_user:
        raise HTTPException(status_code=400, detail="用户不存在")
    if not bcrypt.checkpw(user_dict['password'].encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="密码错误")
    return {"access_token": base64.encodebytes(db_user.name.encode('utf-8'))}
