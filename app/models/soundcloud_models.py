from typing import List, Optional

from pydantic import Field

from app.models import ArtistProfile, Track, Pagination


class SoundcloudProfile(ArtistProfile):
    track_count: Optional[int] = None
    tracks: Optional[List[Track]] = None
    reposts_count: Optional[int] = None
    likes_count: Optional[int] = None

class SoundcloudSearchResult(Pagination):
    profiles: List[SoundcloudProfile] = Field(default_factory=list)
    tracks: List[Track] = Field(default_factory=list)