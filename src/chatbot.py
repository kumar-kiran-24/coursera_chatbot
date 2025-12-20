from src.utils.exception import CustomException
import os
import sys
import re

from groq import Groq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

# --------------------------------------------------------
# SANITIZER
# --------------------------------------------------------

def sanitize_prompt(text: str) -> str:
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e]", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(
        r"(coursera|academic integrity|protected assessment|policy|prohibited)",
        "",
        text,
        flags=re.I,
    )
    return re.sub(r"\s+", " ", text).strip()

# --------------------------------------------------------
# ANSWER EXTRACTOR
# --------------------------------------------------------

def extract_answer(text: str) -> str:
    m = re.search(r"Correct Answer\s*:\s*([A-D])", text, flags=re.I)
    return m.group(1).upper() if m else "No answer found"

# --------------------------------------------------------
# CHATBOT
# --------------------------------------------------------

class ChatBot:
    def __init__(self):
        try:
            api_key = "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"
            if not api_key:
                raise RuntimeError("GROQ_API_KEY missing in Streamlit Secrets")

            self.client = Groq(api_key=api_key)
            self.history = []

        except Exception as e:
            raise CustomException(e, sys)

    def trim_history(self, max_turns=4):
        max_messages = max_turns * 2
        self.history = self.history[-max_messages:]

    def ask(self, user_question: str) -> str:
        cleaned_question = sanitize_prompt(user_question)
        self.trim_history()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """
You are an AI Assistant that generates MCQs.

Rules:
- EXACTLY 4 options (A, B, C, D)
- ONE correct answer
- NO explanations
- Output format only

Format:
Q1. question
A)
B)
C)
D)
Correct Answer: <option>
"""),
            *self.history,
            ("user", "{question}")
        ]).invoke({"question": cleaned_question})

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=prompt.to_messages(),
            temperature=0.2,
        )

        reply = response.choices[0].message.content

        self.history.append(HumanMessage(content=cleaned_question))
        self.history.append(AIMessage(content=reply))

        return reply

    def reset(self):
        self.history = []
