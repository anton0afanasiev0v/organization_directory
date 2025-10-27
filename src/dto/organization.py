from pydantic import BaseModel

from .activity import Activity
from .building import Building


class PhoneBase(BaseModel):
    phone_number: str


class PhoneCreate(PhoneBase):
    pass


class Phone(PhoneBase):
    id: int

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    building_id: int


class OrganizationCreate(OrganizationBase):
    phone_numbers: list[PhoneCreate] = []
    activity_ids: list[int] = []


class OrganizationUpdate(BaseModel):
    name: str | None = None
    building_id: int | None = None
    phone_numbers: list[PhoneCreate] | None = None
    activity_ids: list[int] | None = None


class OrganizationSimple(OrganizationBase):
    id: int

    class Config:
        from_attributes = True


class Organization(OrganizationSimple):
    phone_numbers: list[Phone] = []
    activities: list[Activity] = []
    building: Building

    # Используем строковые аннотации или TYPE_CHECKING
    activities: list["Activity"] = []
    building: "Building"

    class Config:
        from_attributes = True
