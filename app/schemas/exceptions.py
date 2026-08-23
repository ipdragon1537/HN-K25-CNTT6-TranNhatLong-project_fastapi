from fastapi.responses import JSONResponse
from fastapi import Request,status
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
def setup_exceptions_handler(app):
    @app.exception_handler(HTTPException)
    def http_exception_handler(request:Request,exc:HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success":False,
                "code":exc.status_code,
                "message":exc.detail,
                "data":None
            },
        )
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request:Request,exc:RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success":False,
                "code":400,
                "message":"Dữ liệu đầu vào ko hợp lệ",
                "detail":exc.errors()
            },
        )