from pydantic import BaseModel


class ActivityBase(BaseModel):
    name: str
    parent_id: int | None = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True


class ActivityWithChildren(Activity):
    children: list["ActivityWithChildren"] = []


class ActivityTree(Activity):
    level: int
    children: list["ActivityTree"] = []
