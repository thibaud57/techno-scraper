from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from app.models.artist_profile import ArtistProfile


class Track(BaseModel):
    id: int
    title: str
    url: Optional[HttpUrl] = None
    artwork_url: Optional[HttpUrl] = None
    play_count: Optional[int] = None
    download_count: Optional[int] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    labels: Optional[List[ArtistProfile]] = None
    artists: Optional[List[ArtistProfile]] = None
    remixers: Optional[List[ArtistProfile]] = None