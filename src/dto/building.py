from pydantic import BaseModel



class BuildingBase(BaseModel):
    address: str
    latitude: float = None
    longitude: float = None


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True


class CoordinateRange(BaseModel):
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


class RadiusSearch(BaseModel):
    latitude: float
    longitude: float
    radius_km: float
