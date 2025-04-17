from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class Track(BaseModel):
    title: str
    url: Optional[HttpUrl] = None
    artwork_url: Optional[HttpUrl] = None
    play_count: Optional[int] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    labels: Optional[List[str]] = None
    artists: Optional[List[str]] = None
    remixers: Optional[List[str]] = None