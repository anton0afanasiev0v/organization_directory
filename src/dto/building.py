from pydantic import BaseModel

class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True

class BuildingWithOrganizations(Building):
    organizations: list['OrganizationSimple'] = []

class CoordinateRange(BaseModel):
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float

class RadiusSearch(BaseModel):
    latitude: float
    longitude: float
    radius_km: float