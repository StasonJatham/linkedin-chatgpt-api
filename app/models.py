from pydantic import BaseModel


class MessageIn(BaseModel):
    message: str
    web_search: bool = False
    image_gen: bool = False
    deep_research: bool = False


class MessageOut(MessageIn):
    result: str
    mode: str
