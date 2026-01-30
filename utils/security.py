from passlib.context import CryptContext

# 创建密码加密上下文
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

#密码加密
def get_hash_password(password):
    return pwd_context.hash(password)

#密码验证:verify_password返回bool型
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
