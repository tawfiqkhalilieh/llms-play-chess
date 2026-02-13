from fastapi import FastAPI, HTTPException
from mcp_server.models.Move import MoveRequest, MoveResponse
from agents.llm_agents import AGENTS_TYPE, GeminiAgent, OpenAIAgent, LocalAgent
from agents.constants import LLM_AGENT_TYPE

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
            "local": LocalAgent,
    } # type: ignore
    
    if LLM_AGENT_TYPE not in agent_constructors:
        raise HTTPException(status_code=500, detail=f"Unsupported LLM_AGENT_TYPE: {LLM_AGENT_TYPE}")

    try:
        AGENT = agent_constructors[LLM_AGENT_TYPE]() # type: ignore
        print(f"Initialized agent instance: {AGENT.__class__.__name__}")
        
        # Pre-initialize model to catch errors early
        if hasattr(AGENT, "_initialize_model"):
            print("Pre-initializing model...")
            AGENT._initialize_model()
            print("Model pre-initialized.")
            
    except Exception as e:
        print(f"CRITICAL ERROR during agent initialization: {e}")
        raise e

    print(f"Agent setup complete: {AGENT.__class__.__name__}")


