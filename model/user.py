from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: str
    display_name: str
    profile_image: str
    working_on: List[str] = []
    interested_in: List[str] = []
    would_like_to_eat: List[str] = []
    failed_story: List[str] = []
