from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import ArtistProfile, Track


class BandcampEntityType(str, Enum):
    BANDS = "b"  # Artistes et labels
    TRACKS = "t"  # Pistes


class BandcampBandProfile(ArtistProfile):
    location: Optional[str] = None
    genre: Optional[str] =  None


class BandcampSearchResult(BaseModel):
    bands: List[BandcampBandProfile] = Field(default_factory=list)
    tracks: List[Track] = Field(default_factory=list)
