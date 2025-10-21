from pydantic import BaseModel
from typing import List, Optional

class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True

class ActivityWithChildren(Activity):
    children: List['ActivityWithChildren'] = []

class ActivityTree(Activity):
    level: int
    children: List['ActivityTree'] = []