from pydantic import BaseModel


class ApplicationSnapshot(BaseModel):
    """Lightweight application context attached to operational events."""

    id: str
    name: str
    tags: dict[str, str]


class ServiceSnapshot(BaseModel):
    """Lightweight service context attached to operational events."""

    id: str
    name: str
    tags: dict[str, str]


class EnvironmentSnapshot(BaseModel):
    """Lightweight environment context attached to operational events."""

    id: str
    name: str
