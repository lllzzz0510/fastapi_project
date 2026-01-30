from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from crud import users
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse
from utils.response import success_response

router = APIRouter(prefix="/api/user",tags=["user"])

@router.post("/register")
async def register_user(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
    existing_user = await users.get_user_by_username(db,user_data.username)
    if existing_user:
        raise HTTPException(status_code=400,detail="用户名已存在")
    user=await users.create_user(db,user_data)
    token=await users.create_token(db,user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #     "token": token,
    #     "userInfo": {
    #     "id": user.id,
    #     "username": user.username,
    #     "avatar": user.avatar,
    #     "bio": user.bio,
    #         }
    #     }
    # }
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(msg="注册成功",data=response_data)


@router.post("/login")
async def login(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
    #登录逻辑：验证用户是否存在--》验证密码--》生成token--》响应结果
    user=await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")
    token=await users.create_token(db,user.id)
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(msg="登录成功",data=response_data)



