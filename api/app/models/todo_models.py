from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseTodo(BaseModel):
    task: str
    completed: bool

class ResponseTodo(BaseTodo):
    id: str
    created_at: datetime
    updated_at: datetime

class CreateTodo(BaseModel):
    task: str

class UpdateTodo(BaseModel):
    task: Optional[str] = None
    completed: Optional[bool] = None