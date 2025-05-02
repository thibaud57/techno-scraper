from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from app.models import ArtistProfile


class Release(BaseModel):
    id: int
    title: str
    url: Optional[HttpUrl] = None
    artwork_url: Optional[HttpUrl] = None
    release_date: Optional[str] = None
    track_count: Optional[int] = None
    label: Optional[ArtistProfile] = None
    artists: Optional[List[ArtistProfile]] = None
