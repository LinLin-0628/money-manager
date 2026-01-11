from enum import Enum

class SensitiveField(str, Enum):
    EMAIL = "email"
    NAME = "name"
    ID = "uuid"
