from typing import Any

from pydantic import BaseModel


class PlanStep(BaseModel):

    id: int

    task: str

    agent: str

    requires_tool: bool = False

    depends_on: list[int] = []


class Plan(BaseModel):

    steps: list[PlanStep]