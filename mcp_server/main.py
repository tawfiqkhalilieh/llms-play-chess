from fastapi import FastAPI, HTTPException
from models.Move import MoveRequest, MoveResponse
from agents.llm_agents import AGENTS_TYPE, GeminiAgent, OpenAIAgent
from constants import LLM_AGENT_TYPE

app: FastAPI = FastAPI()

AGENT: AGENTS_TYPE | None = None

@app.post("/move", response_model=MoveResponse)
async def get_move(request: MoveRequest):
    if AGENT is None:
        raise HTTPException(status_code=401, detail="LLM Agent not initialized.")
    
    try:
        move, comment, explanation = AGENT.get_move(
            request.pgn, request.possible_moves, request.context
        )

        return MoveResponse(
            move=move,
            comment=comment,
            explanation=explanation,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.on_event("startup")
async def startup_event():

    # TODO: add more patterns
    global AGENT

    agent_constructors: dict[str, AGENTS_TYPE] = { 
            "gemini": GeminiAgent,
            "openai": OpenAIAgent,
    } # type: ignore
    
    if LLM_AGENT_TYPE not in agent_constructors:
        raise HTTPException(status_code=500, detail=f"Unsupported LLM_AGENT_TYPE: {LLM_AGENT_TYPE}")

    AGENT = agent_constructors[LLM_AGENT_TYPE]() # type: ignore

    print(f"Initialized agent: {AGENT.__class__.__name__}")


