from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from app.models import SocialLink


class ArtistProfile(BaseModel):
    name: str
    url: HttpUrl
    bio: Optional[str] = None
    followers_count: Optional[int] = None
    location: Optional[str] = None
    social_links: Optional[List[SocialLink]] = None
    avatar_url: Optional[HttpUrl] = None
