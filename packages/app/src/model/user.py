from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    username: str
    full_name: str
    created_datetime: datetime
