from marshmallow import ValidationError

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum


def validate_input(data: dict, schema) -> dict:
    '''Validate given data with given Schema. If data is not valid abort 422 Response or 400 if no data provided.'''
    if not data:
        raise APIException('No data provided.',
                           status=StatusEnum.BAD_REQUEST.name)

    try:
        validate_data = schema().load(data)
    except ValidationError:
        raise APIException('Request validation has failed',
                           status=StatusEnum.ENPROCESSABLE_ENTITY.name)

    return validate_data
