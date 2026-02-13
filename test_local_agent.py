from agents.llm_agents import LocalAgent
try:
    print("Initializing LocalAgent...")
    agent = LocalAgent()
    print("Agent initialized. loading model...")
    agent._initialize_model()
    print("Model loaded.")
    move, comment, explanation = agent.get_move(
        "", ["e2e4", "d2d4"], "Start of game"
    )
    print(f"Move: {move}")
    print(f"Comment: {comment}")
    print(f"Explanation: {explanation}")
except Exception as e:
    print(f"Error: {e}")
