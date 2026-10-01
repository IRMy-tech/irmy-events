from pydantic import BaseModel


class UserRef(BaseModel):
    """Person reference used in operational events: {id, firstName, lastName, email}."""

    id: str
    firstName: str
    lastName: str
    email: str


class NamedRef(BaseModel):
    """Generic named-entity reference: {id, name}."""

    id: str
    name: str
