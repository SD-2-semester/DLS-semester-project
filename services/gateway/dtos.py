from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)
