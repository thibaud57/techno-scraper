from typing import List, Optional

from pydantic import Field

from app.models import ArtistProfile, Pagination, Release


class BandcampProfile(ArtistProfile):
    releases: Optional[List[Release]] = None


class BandcampSearchResult(Pagination):
    profiles: List[BandcampProfile] = Field(default_factory=list)
    releases: List[Release] = Field(default_factory=list)
