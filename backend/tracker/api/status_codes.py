from enum import Enum


class StatusEnum(Enum):
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    ENPROCESSABLE_ENTITY = 422
