from typing import List, Optional

from pydantic import Field

from app.models import ArtistProfile, Track, Pagination

# Constantes pour l'API SoundCloud
SOUNDCLOUD_BASE_URL = "https://soundcloud.com"
SOUNDCLOUD_API_URL = "https://api-v2.soundcloud.com"
SOUNDCLOUD_CLIENT_ID = "EjkRJG0BLNEZquRiPZYdNtJdyGtTuHdp"


class SoundcloudProfile(ArtistProfile):
    id: int
    tracks: Optional[List[Track]] = None


class SoundcloudSearchResult(Pagination):
    profiles: List[SoundcloudProfile] = Field(default_factory=list)
    tracks: List[Track] = Field(default_factory=list)