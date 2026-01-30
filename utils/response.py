from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse


def success_response(msg:str="success",data=None):
    content={
        "code":200,
        "msg":msg,
        "data":data
    }
    return JSONResponse(content=jsonable_encoder(content))
