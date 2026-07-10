from pydantic import BaseModel


class TopicFrequency(BaseModel):
    name: str
    mention_count: int
