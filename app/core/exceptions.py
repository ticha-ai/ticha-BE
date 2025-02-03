from fastapi import HTTPException, status


class KakaoAPIException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 회원입니다."
        )


class ValidationError(HTTPException):
    def __init__(
        self, code: str, message: str, details: dict = None, status_code: int = 400
    ):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details},
        )
