from pydantic import BaseModel
from typing import List, Optional

class Pagination(BaseModel):
    total: int
    limit: int
    offset: int
