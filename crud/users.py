import uuid
from datetime import datetime, timedelta
from time import sleep

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest
from utils import security


#根据用户名查询数据库
async def get_user_by_username(db:AsyncSession,username:str):
    query=select(User).where(User.username==username)
    res=await db.execute(query)
    return res.scalar_one_or_none()

#创建用户,passlib加密密码
async def create_user(db:AsyncSession,user_data:UserRequest):
    # 加密密码
    hashed_password=security.get_hash_password(user_data.password)
    user=User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) # 刷新数据库中的用户对象，确保包含数据库生成的 ID
    return user

#生成Token
async def create_token(db:AsyncSession,user_id:int):
    # 生成Token+生成过期时间，查询当前是否存在
    token=str(uuid.uuid4())
    #timedelta（days，hours，minutes，seconds）
    expires_at=datetime.now()+timedelta(days=7)
    query=select(UserToken).where(UserToken.user_id==user_id)
    res=await db.execute(query)
    user_token=res.scalar_one_or_none()

    if user_token:
        user_token.token=token
        user_token.expires_at=expires_at
    else:
        user_token=UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
        await db.commit()
    return token

async def authenticate_user(db:AsyncSession,username:str,password:str):
    user=await get_user_by_username(db,username)
    if not user:
        return None
    if not security.verify_password(password,user.password):
        return None
    return user

async def get_user_by_token(db:AsyncSession,token:str):
    query=select(UserToken).where(UserToken.token==token)
    res=await db.execute(query)
    db_token=res.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    query=select(User).where(User.id == db_token.user_id)
    res=await db.execute(query)
    return res.scalar_one_or_none()


