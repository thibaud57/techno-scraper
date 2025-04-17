from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from app.models import Track


class Release(BaseModel):
    title: str
    url: Optional[HttpUrl] = None
    artwork_url: Optional[HttpUrl] = None
    release_date: Optional[str] = None
    label: Optional[str] = None
    tracks: Optional[List[Track]] = None
    artists: Optional[List[str]] = None
    genre: Optional[str] = None