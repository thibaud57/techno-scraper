from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, HttpUrl


class PlatformEnum(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    BEATPORT = "beatport"
    BANDCAMP = "bandcamp"
    WEBSITE = "website"


class SocialLink(BaseModel):
    platform: PlatformEnum
    url: HttpUrl
    
    @staticmethod
    def from_service(name: str, url: str) -> Optional['SocialLink']:
        if not name or not url:
            return None
            
        name = name.lower()
        
        name_to_platform: Dict[str, PlatformEnum] = {
            "facebook": PlatformEnum.FACEBOOK,
            "instagram": PlatformEnum.INSTAGRAM,
            "spotify": PlatformEnum.SPOTIFY,
            "soundcloud": PlatformEnum.SOUNDCLOUD,
            "beatport": PlatformEnum.BEATPORT,
            "bandcamp": PlatformEnum.BANDCAMP,
            "website": PlatformEnum.WEBSITE,
        }
        
        platform = name_to_platform.get(name)
        if not platform:
            return None
            
        try:
            return SocialLink(platform=platform, url=url)
        except Exception:
            return None
