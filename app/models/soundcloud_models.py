from typing import List, Optional

from pydantic import Field

from app.models import ArtistProfile, Track, Pagination
from app.models.social_link import SocialLink


class SoundcloudProfile(ArtistProfile):
    bio: Optional[str] = None
    location: Optional[str] = None
    followers_count: Optional[int] = None
    tracks: Optional[List[Track]] = None
    social_links: Optional[List[SocialLink]] = None



class SoundcloudSearchResult(Pagination):
    profiles: List[SoundcloudProfile] = Field(default_factory=list)
    tracks: List[Track] = Field(default_factory=list)