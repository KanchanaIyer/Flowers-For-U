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
