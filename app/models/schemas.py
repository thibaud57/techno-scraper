from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseModel):
    message: str = "Opération réussie"

class Pagination(BaseModel):
    total_results: int = 0
    page: int = 1
    has_more: bool = False
