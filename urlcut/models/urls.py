from datetime import datetime
from typing import List

from pydantic import BaseModel, HttpUrl


class UrlCreateData(BaseModel):
    name: str
    description: str = None
    url: HttpUrl
    notActiveAfter: datetime = None
    labels: List[str] = []
    creator: str = None
    barcode: bool = False
