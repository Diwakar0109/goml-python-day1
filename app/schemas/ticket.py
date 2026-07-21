from datetime import datetime, UTC

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from typing_extensions import Literal


class CreateTicketRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    priority: Literal["low", "medium", "high"] = "medium"

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be blank")
        return value


class UpdateTicketRequest(BaseModel):
    title: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    status: Optional[
        Literal["open", "in_progress", "resolved"]
    ] = None
    assignee: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be blank")

        return value


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    title: str
    priority: Literal["low", "medium", "high"]
    status: Literal["open", "in_progress", "resolved"] = "open"
    created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC)
)

    @computed_field
    @property
    def is_resolved(self) -> bool:
        return self.status == "resolved"