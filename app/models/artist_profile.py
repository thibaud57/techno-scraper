from typing import List, Optional

from pydantic import BaseModel, HttpUrl

class ArtistProfile(BaseModel):
    id: int
    name: str
    url: HttpUrl
    avatar_url: Optional[HttpUrl] = None
