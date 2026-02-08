import os
import json
import abc
import google.generativeai as genai
from agents.constants import OPENAI_API_KEY, GEMINI_MODEL, GEMINI_API_KEY
# Placeholder for OpenAI and other LLM libraries
# from openai import OpenAI 

class BaseAgent(abc.ABC):
    @abc.abstractmethod
    def get_move(self, pgn: str, possible_moves: list[str], context: str) -> tuple[str, str, str]:
        pass

class GeminiAgent(BaseAgent):
    def __init__(self):
        self.genai = genai
        self.model = None
        self.configured = False

    def _initialize_model(self):
        self.genai.configure(api_key=GEMINI_API_KEY) # type: ignore
        self.model = self.genai.GenerativeModel(GEMINI_MODEL) # type: ignore
        self.configured = True

    def get_move(self, pgn: str, possible_moves: list[str], context: str) -> tuple[str, str, str]:
        if not self.configured:
            self._initialize_model()

        prompt = f"""
You are a world-class chess AI.
Your goal is to choose the best move to play in the current position.
You will be given the PGN of the game so far, a list of possible moves, and some context.
You must choose one of the possible moves.

**PGN:**
{pgn}

**Possible Moves:**
{', '.join(possible_moves)}

**Context:**
{context}

You must return a JSON object with the following format:
{{
    "move": "e2e4",
    "comment": "A classic opening, let's see where this goes!",
    "explanation": "Moving the king's pawn forward two squares to control the center of the board."
}}

The "move" must be one of the possible moves.
The "comment" should be a cool, short comment about the move (max 20 words).
The "explanation" should be a longer, more detailed explanation of the position and your plan.

Now, it's your turn. What is the best move?
"""

        try:
            response = self.model.generate_content(prompt) # type: ignore
            # Ensure the response text is not empty before stripping
            if not response.text:
                raise ValueError("Gemini API returned an empty response.")
                
            response_json = json.loads(response.text.strip("`json\n "))
            
            if not all(key in response_json for key in ["move", "comment", "explanation"]):
                raise ValueError("Gemini API response missing expected keys (move, comment, explanation).")

            if response_json["move"] not in possible_moves:
                raise ValueError(f"Gemini API returned an illegal move: {response_json['move']}")

            return response_json["move"], response_json["comment"], response_json["explanation"]
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON from Gemini API response: {e}. Raw response: {response.text}")
        except Exception as e:
            raise ValueError(f"Error calling Gemini API: {e}")

# NOTE: OpenAI agent is incomplete
# Example of how an OpenAI agent might look (untested, placeholder)
class OpenAIAgent(BaseAgent):
    def __init__(self):
        # self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        pass # Placeholder

    def get_move(self, pgn: str, possible_moves: list[str], context: str) -> tuple[str, str, str]:
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable not set for OpenAIAgent.")
        
        # This is a placeholder for the actual OpenAI API call
        print("OpenAI agent not fully implemented. Returning a random move.")
        import random
        return random.choice(possible_moves), "I am an OpenAI agent (placeholder).", "This is a placeholder explanation."



AGENTS_TYPE = GeminiAgent | OpenAIAgent # TODO: update this when more agents are added

