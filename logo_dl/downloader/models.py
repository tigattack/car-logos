from pydantic import BaseModel


class Manufacturer(BaseModel):
    name: str
    url: str


class LogoImage(BaseModel):
    source: str
    path: str


class ManufacturerLogo(BaseModel):
    name: str
    slug: str
    image: LogoImage
