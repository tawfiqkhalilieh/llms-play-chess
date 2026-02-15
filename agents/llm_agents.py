import os
import json
import abc
import time
import google.generativeai as genai
from llama_cpp import Llama
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError, APITimeoutError, BadRequestError
from agents.constants import OPENAI_API_KEY, OPENAI_MODEL, GEMINI_MODEL, GEMINI_API_KEY, LOCAL_MODEL_PATH

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

class OpenAIAgent(BaseAgent):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    def _get_completion_with_retry(self, prompt: str, max_retries: int = 5, initial_delay: float = 0.5) -> str:
        delay = initial_delay
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant playing chess."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("OpenAI API returned empty content.")
                return content
            except RateLimitError as e:
                print(f"Rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            except (APIConnectionError, APITimeoutError) as e:
                print(f"Connection error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            except (AuthenticationError, BadRequestError) as e:
                # Do not retry on auth or bad request errors
                raise e
            except Exception as e:
                print(f"Unexpected error calling OpenAI API: {e}")
                # For other unexpected errors, we might want to retry or fail.
                # Here, we'll retry a few times just in case it's transient.
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2
        
        raise RuntimeError(f"Failed to get completion after {max_retries} retries.")

    def get_move(self, pgn: str, possible_moves: list[str], context: str) -> tuple[str, str, str]:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set or empty in constants.")

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
            response_text = self._get_completion_with_retry(prompt)
            response_json = json.loads(response_text)
            
            if not all(key in response_json for key in ["move", "comment", "explanation"]):
                raise ValueError("OpenAI API response missing expected keys (move, comment, explanation).")

            if response_json["move"] not in possible_moves:
                # Basic validation failed, let's try to pick a valid move if the reasoning is sound,
                # or just fail. For now, fail.
                raise ValueError(f"OpenAI API returned an illegal move: {response_json['move']}")

            return response_json["move"], response_json["comment"], response_json["explanation"]

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON from OpenAI API response: {e}")
        except Exception as e:
            raise ValueError(f"Error in OpenAIAgent: {e}")
        
class LocalAgent(BaseAgent):
    def __init__(self):
        self.llm = None
        self.model_path = LOCAL_MODEL_PATH

    def _initialize_model(self):
        if not os.path.exists(self.model_path):
            raise ValueError(f"Model file not found at {self.model_path}")
        # Initialize the model. n_ctx is context window size.
        print(f"Loading model from {self.model_path}...")
        self.llm = Llama(model_path=self.model_path, n_ctx=512, verbose=False, n_threads=1)
        print("Model loaded successfully.")

    def get_move(self, pgn: str, possible_moves: list[str], context: str) -> tuple[str, str, str]:
        if self.llm is None:
            self._initialize_model()

        # Construct a prompt suitable for an instruction-tuned model
        prompt = f"""<|im_start|>system
        You are a world-class chess AI.
Your goal is to choose the best move to play in the current position.
You will be given the PGN of the game so far, a list of possible moves, and some context.
You must choose one of the possible moves.

        You must return a JSON object with the following format:
        {{
            "move": "e2e4",
            "comment": "A classic opening.",
            "explanation": "Moving the king's pawn forward."
        }}
        <|im_end|>
        <|im_start|>user
        **PGN:**
        {pgn}

        **Possible Moves:**
        {', '.join(possible_moves)}

        **Context:**
        {context}

        **Move Count:**
        {pgn.count('.')}

        What is the best move? Use chess terminology and sound knowledgeable. Return ONLY the JSON object.
        <|im_end|>
        <|im_start|>assistant
        """
        try:
            output = self.llm(
                prompt,
                max_tokens=512,
                stop=["<|im_end|>"],
                echo=False,
                temperature=0.1 # Low temperature for more deterministic output
            )
            
            response_text = output['choices'][0]['text']
            # Clean up potential markdown code blocks
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_json = json.loads(response_text.strip())

            if not all(key in response_json for key in ["move", "comment", "explanation"]):
                raise ValueError("Local model response missing keys.")

            if response_json["move"] not in possible_moves:
                 # Fallback: simple heuristic or random if model hallucinates an illegal move
                 # For now, just raise error
                raise ValueError(f"Local model returned illegal move: {response_json['move']}")

            return response_json["move"], response_json["comment"], response_json["explanation"]

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON from local model: {e}. Raw: {response_text}")
        except Exception as e:
             raise ValueError(f"Error in LocalAgent: {e}")

AGENTS_TYPE = GeminiAgent | OpenAIAgent | LocalAgent