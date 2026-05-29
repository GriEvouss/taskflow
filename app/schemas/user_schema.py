from marshmallow import Schema, fields


class UserSchema(Schema):
    """Схема для сериализации пользователя."""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """Схема для валидации данных при создании пользователя."""
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    role = fields.Str(load_default='user')


class UserLoginSchema(Schema):
    """Схема для валидации данных при входе пользователя."""
    username = fields.Str(required=True)
    password = fields.Str(required=True)