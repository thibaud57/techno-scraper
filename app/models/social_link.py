from pydantic import BaseModel, HttpUrl


class SocialLink(BaseModel):
    platform: str
    url: HttpUrl
