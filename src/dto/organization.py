from pydantic import BaseModel
from typing import List, Optional
from .building import Building
from .activity import Activity

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
    phone_numbers: List[PhoneCreate] = []
    activity_ids: List[int] = []

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    building_id: Optional[int] = None
    phone_numbers: Optional[List[PhoneCreate]] = None
    activity_ids: Optional[List[int]] = None

class OrganizationSimple(OrganizationBase):
    id: int

    class Config:
        from_attributes = True

class Organization(OrganizationSimple):
    phone_numbers: List[Phone] = []
    activities: List[Activity] = []
    building: Building

    class Config:
        from_attributes = True

# # Для избежания circular imports
# from app.schemas.building import BuildingWithOrganizations
# from app.schemas.activity import ActivityWithChildren
#
# ActivityWithChildren.update_forward_refs()
# ActivityTree.update_forward_refs()
# BuildingWithOrganizations.update_forward_refs()