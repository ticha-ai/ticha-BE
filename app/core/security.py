from typing import Dict


# mock data
def get_current_user() -> Dict:
    """
    나중에 실제 인증 로직으로 대체
    """
    return {"user_id": 1, "username": "dummy_user", "email": "dummy@example.com"}
