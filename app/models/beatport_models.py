from typing import List, Optional

from pydantic import Field

from app.models import ArtistProfile, Release, Pagination, Track


class BeatportProfile(ArtistProfile):
    releases: Optional[List[Release]] = None

class BeatportSearchResult(Pagination):
    profiles: List[BeatportProfile] = Field(default_factory=list)
    tracks: List[Track] = Field(default_factory=list)
    releases: List[Release] = Field(default_factory=list)