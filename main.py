from fastapi import FastAPI
from sqlalchemy.testing.suite.test_reflection import users
from starlette.middleware.cors import CORSMiddleware
from routers import news,users
from utils.exception_handlers import register_exception_handlers

#cors中间件要同源，协议端口要一致
app = FastAPI()

#注册异常处理
register_exception_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许所有来源
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"], # 允许所有方法
    allow_headers=["*"], # 允许所有头信息
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/c_hello")
async def c_hello():
    return {"message": "Hello World"}

app.include_router(news.router)
app.include_router(users.router)