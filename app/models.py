from typing import Optional

from pydantic import BaseModel


class Mirror(BaseModel):
    address: Optional[str]
    location: Optional[str]


class MirrorWithPrivInfo(Mirror):
    owner: Optional[str]
    owner_location: Optional[str]
    contact: Optional[str]


class Message(BaseModel):
    success: bool
    message: str
