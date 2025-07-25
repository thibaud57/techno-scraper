from enum import Enum, auto
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import ArtistProfile, Release, Pagination, Track


class BeatportEntityType(Enum):
    SEARCH = "search"
    ARTIST = "artist"
    RELEASE = "release"
    TRACK = "track"
    LABEL = "label"


class BeatportReleaseEntityType(str, Enum):
    ARTIST = "artist"
    LABEL = "label"


class BeatportFacetItem(BaseModel):
    name: str
    count: int


class BeatportFacetFields(BaseModel):
    genre: List[BeatportFacetItem] = Field(default_factory=list)


class BeatportFacets(BaseModel):
    fields: BeatportFacetFields


class BeatportReleasesResult(BaseModel):
    releases: List[Release] = Field(default_factory=list)
    facets: Optional[BeatportFacets] = None


class BeatportProfile(ArtistProfile):
    releases: Optional[List[Release]] = None


class BeatportSearchResult(Pagination):
    artists: List[ArtistProfile] = Field(default_factory=list)
    tracks: List[Track] = Field(default_factory=list)
    releases: List[Release] = Field(default_factory=list)
    labels: List[ArtistProfile] = Field(default_factory=list)