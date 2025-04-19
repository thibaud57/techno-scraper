from typing import List, Optional

from pydantic import Field

from app.models import ArtistProfile, Track, Pagination


class SoundcloudProfile(ArtistProfile):
    id: int
    tracks: Optional[List[Track]] = None

class SoundcloudSearchResult(Pagination):
    profiles: List[SoundcloudProfile] = Field(default_factory=list)
    tracks: List[Track] = Field(default_factory=list)