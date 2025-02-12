from typing import List

from pydantic import BaseModel


class StarUpdate(BaseModel):
    is_starred: bool


class StarredProblem(BaseModel):
    problem_id: int
    is_starred: bool


class StarredProblemsResponse(BaseModel):
    starred_problems: List[StarredProblem]
