from marshmallow import Schema, fields, validate, validates, ValidationError


class TaskSchema(Schema):
    """Схема для сериализации задачи."""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    status = fields.Str()
    project_id = fields.Int()
    assignee_id = fields.Int(allow_none=True)
    assignee_username = fields.Str(dump_only=True)
    parent_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TaskCreateSchema(Schema):
    """Схема для валидации данных при создании задачи."""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.Str(load_default='')
    project_id = fields.Int(required=True)
    assignee_id = fields.Int(allow_none=True)
    status = fields.Str(load_default='todo')
    parent_id = fields.Int(allow_none=True)

    @validates('title')
    def validate_title(self, value):
        if not value or not value.strip():
            raise ValidationError('Task title cannot be empty')

    @validates('status')
    def validate_status(self, value):
        valid_statuses = ['todo', 'in_progress', 'done']
        if value not in valid_statuses:
            raise ValidationError(f'Status must be one of: {", ".join(valid_statuses)}')


class TaskUpdateSchema(Schema):
    """Схема для валидации данных при обновлении задачи."""
    title = fields.Str(
        validate=validate.Length(min=1, max=200)
    )
    description = fields.Str()
    status = fields.Str()
    assignee_id = fields.Int(allow_none=True)
    parent_id = fields.Int(allow_none=True)

    @validates('status')
    def validate_status(self, value):
        if value:
            valid_statuses = ['todo', 'in_progress', 'done']
            if value not in valid_statuses:
                raise ValidationError(f'Status must be one of: {", ".join(valid_statuses)}')