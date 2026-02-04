from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "REQUEST_ERROR"
    payload = {
        "error": {
            "code": detail,
            "message": detail.replace("_", " ").lower(),
            "details": {"status_code": exc.status_code},
        }
    }
    return JSONResponse(status_code=exc.status_code, content=payload)


def unhandled_exception_handler(request: Request, exc: Exception):
    payload = {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "internal error",
            "details": {},
        }
    }
    return JSONResponse(status_code=500, content=payload)
