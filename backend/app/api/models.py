from pydantic import BaseModel


class ChatInput(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str


class BuildDatasetRequest(BaseModel):
    number_of_characters: int


class BuildDatasetResponse(BaseModel):
    number_of_characters: int
