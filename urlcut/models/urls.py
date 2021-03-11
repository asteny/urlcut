from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class UrlCreateData(BaseModel):
    name: str
    description: str = ""
    url: HttpUrl
    active: bool = True
    notActiveAfter: Optional[datetime] = None
    labels: List[str] = []
    creator: str = ""
    qr: bool = False


class UrlUpdateData(BaseModel):
    name: str
    description: str
    active: bool
    notActiveAfter: Optional[datetime] = None
    labels: List[str]
    creator: str
