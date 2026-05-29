from marshmallow import Schema, fields, validate, validates, ValidationError


class ProjectSchema(Schema):
    """Схема для сериализации проекта."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    owner_id = fields.Int(dump_only=True)
    owner_username = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProjectCreateSchema(Schema):
    """Схема для валидации данных при создании проекта."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='Project name must be 1-100 characters')
    )
    description = fields.Str(load_default='')

    @validates('name')
    def validate_name(self, value):
        if not value or not value.strip():
            raise ValidationError('Project name cannot be empty')


class ProjectUpdateSchema(Schema):
    """Схема для валидации данных при обновлении проекта."""
    name = fields.Str(
        validate=validate.Length(min=1, max=100, error='Project name must be 1-100 characters')
    )
    description = fields.Str()