from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/index")
async def serve_index_page():
    """
    index.html 파일 반환
    """
    return FileResponse("app/public/index.html")


@router.get("/login")
async def serve_login_page():
    """
    로그인 페이지 반환
    """
    return FileResponse("app/public/login.html")
