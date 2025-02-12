from pydantic import BaseModel


class StarUpdate(BaseModel):
    is_starred: bool
