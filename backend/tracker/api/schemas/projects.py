from marshmallow import Schema, validates
from marshmallow.fields import Str
from marshmallow.validate import Length


class ProjectCreationSchema(Schema):
    title = Str(required=True, validate=Length(min=4, max=32))
    description = Str(required=False, validate=Length(min=0, max=128))

class TitleDuplicationCheckSchema(Schema):
    title = Str(required=True, validate=Length(min=4, max=32))