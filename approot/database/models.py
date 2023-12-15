from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: int
    description: str
    stock: int
    location: str = None
    product_id: int = None

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(**data)

    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'stock': self.stock,
            'location': self.location,
            'product_id': self.product_id
        }


@dataclass
class Filter:
    field: str
    rule: str
    value: str
    negate: bool = False
    comparator: str = "AND"

    valid_comparison_operators = ['AND', 'OR']

    def __post_init__(self):
        if self.comparator not in self.valid_comparison_operators:
            raise ValueError(f"Invalid comparator: {self.comparator}. Must be one of {self.valid_comparison_operators}")

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
            'value': self.value,
            'negate': self.negate,
            'comparator': self.comparator
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
