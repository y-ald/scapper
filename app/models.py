from typing import List, Optional

from pydantic import BaseModel


class Author(BaseModel):
    id: str
    name: str
    created_at: str
    followers_count: Optional[int]
    following_count: Optional[int]


class Post(BaseModel):
    author_id: str
    text: str
    timestamp: str
    likes: int
    reposts: int
    comments: int
    media_urls: List[str]
    media_local_paths: List[str]
