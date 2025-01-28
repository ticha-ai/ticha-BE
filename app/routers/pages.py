from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


from pathlib import Path

from fastapi import HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent


@router.get("/index")
async def serve_index_page():
    """
    index.html 파일 반환
    """
    file_path = BASE_DIR / "public" / "index.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Index page not found")
    return FileResponse(file_path)


@router.get("/login")
async def serve_login_page():
    """
    로그인 페이지 반환
    """
    return FileResponse("app/public/login.html")
