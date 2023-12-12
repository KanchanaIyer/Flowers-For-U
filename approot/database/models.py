from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    description: str


@dataclass
class Filter:
    field: str
    rule: str
    value: str

    def __str__(self):
        return f"{self.field} {self.rule} {self.value}"

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(**data)

    def to_dict(self):
        return {
            'field': self.field,
            'rule': self.rule,
            'value': self.value
        }


@dataclass
class User:
    user_id: int
    username: str
    email: str
    is_admin: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        if data.get('password'):
            data.pop('password') # I don't want to have the user's password in the session even if it is hashed
        return cls(**data)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }
