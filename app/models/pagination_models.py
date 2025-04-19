from enum import Enum

from pydantic import BaseModel


class LimitEnum(int, Enum):
    ONE = 1
    FIVE = 5
    TEN = 10
    TWENTY_FIVE = 25
    FIFTY = 50
    HUNDRED = 100


class Pagination(BaseModel):
    total_results: int = 0
    page: int = 1
    limit: LimitEnum = LimitEnum.TEN
    