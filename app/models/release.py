from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from app.models import Track, ArtistProfile


class Release(BaseModel):
    id: int
    title: str
    url: Optional[HttpUrl] = None
    artwork_url: Optional[HttpUrl] = None
    release_date: Optional[str] = None
    label: Optional[ArtistProfile] = None
    tracks: Optional[List[Track]] = None
    artists: Optional[List[ArtistProfile]] = None
    genre: Optional[str] = None