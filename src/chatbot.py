from src.utils.exception import CustomException


import os
import sys
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("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"),
    model="openai/gpt-oss-20b",
    streaming=True
)

# --------------------------------------------------------
# SUPER SANITIZER (removes ALL Coursera integrity content)
# --------------------------------------------------------

def sanitize_prompt(text: str) -> str:
    """
    FULL CLEANER — removes:
    - Coursera academic integrity blocks (full or partial)
    - hidden text injected via copy/paste
    - zero-width characters
    - HTML hidden spans
    - formatting artefacts
    """

    # 1) Remove invisible zero-width characters
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e]", "", text)

    # 2) Remove HTML hidden elements
    text = re.sub(r"<.*?display\s*:\s*none.*?>.*?</.*?>", "", text, flags=re.I | re.S)
    text = re.sub(r"<span.*?hidden.*?>.*?</span>", "", text, flags=re.I | re.S)

    # 3) Remove FULL Coursera block
    text = re.sub(
        r"You are a helpful AI assistant.*?related topics\.",
        "",
        text,
        flags=re.I | re.S,
    )

    # 4) Remove partial Coursera text
    text = re.sub(
        r"(coursera|academic integrity|protected assessment|policy|prohibited|disabled|sole function|cannot interact|assessment pages)",
        "",
        text,
        flags=re.I | re.S,
    )

    # 5) Clean extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# --------------------------------------------------------
# Extract Only the Correct Answer
# --------------------------------------------------------

def extract_answer(text: str) -> str:
    """
    Extract only the correct answer letter from LLM output.
    Example: "Correct Answer: A"
    """
    m = re.search(r"Correct Answer\s*:\s*([A-D])", text, flags=re.I)
    if m:
        return m.group(1).upper()
    return "No answer found"




class ChatBot:
    try:
        # logging.info("chat bot ")

        def __init__(self):
            self.history = []

        # Trim chat history (avoid overload)
        def trim_history(self, max_turns=4):
            max_messages = max_turns * 2  # user+AI per turn
            if len(self.history) > max_messages:
                self.history = self.history[-max_messages:]

        # Clean all past history
        def clean_history(self):
            cleaned = []
            for msg in self.history:
                if isinstance(msg, HumanMessage):
                    cleaned.append(HumanMessage(content=sanitize_prompt(msg.content)))
                else:
                    cleaned.append(msg)
            self.history = cleaned

        # MAIN ASK FUNCTION
        def ask(self, user_question):

            # Clean the incoming question
            cleaned_question = sanitize_prompt(user_question)

            print("Original Question :", user_question)
            print("Cleaned Question  :", cleaned_question)

            # Clean + Trim history
            self.clean_history()
            self.trim_history(max_turns=4)

            # System prompt for MCQ generation
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """
You are an AI Assistant that generates high-quality Multiple Choice Questions (MCQs).

Task:
- Create MCQs based on the user's input text.
- Each question MUST have EXACTLY 4 options: A, B, C, D.
- Only ONE correct answer.
- Do NOT add explanations.
- Do NOT add extra text.

Output format:
Q1. question
A)
B)
C)
D)
Correct Answer: <option>=answer

Rules:
- No markdown.
- No explanations.
- Clean MCQ format only.
                """),
                *self.history,
                ("user", "{question}")
            ])

            final_prompt = prompt_template.invoke({"question": cleaned_question})

            # Call Groq LLM
            response = llm.invoke(final_prompt.to_messages())
            bot_reply = response.content

            # Save CLEANED user message + bot reply
            self.history.append(HumanMessage(content=cleaned_question))
            self.history.append(AIMessage(content=bot_reply))

            # logging.info("Response generated successfully")

            return bot_reply

        def reset(self):
            self.history = []

    except Exception as e:
        CustomException(e, sys)



if __name__ == "__main__":
    bot = ChatBot()
    output = bot.ask("1. Example input here...")
    print(output)
    print("ANSWER ONLY:", extract_answer(output))
