from pydantic import BaseModel

class MoveRequest(BaseModel):
    pgn: str
    possible_moves: list[str]
    context: str



class MoveResponse(BaseModel):
    move: str
    comment: str
    explanation: str

