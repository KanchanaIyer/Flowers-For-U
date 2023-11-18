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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
