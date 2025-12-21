import streamlit as st
from src.chatbot import ChatBot

st.set_page_config(
    page_title=" Chatbot",
    page_icon="",
    layout="centered"
)

st.title(" Chatbot")
st.write("GIVE THE QUESTION WITH OPTIONS")

@st.cache_resource
def load_bot():
    return ChatBot()

###


bot = load_bot()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask your question:")

if st.button("Ask"):
    if user_input.strip():
        answer = bot.ask(user_input)

        st.session_state.chat_history.append(
            ("You", user_input)
        )
        st.session_state.chat_history.append(
            ("Bot", answer)
        )

for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from src.chatbot import ChatBot   # Your chatbot class

# app = FastAPI()

# # Allow frontend to access backend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],       # You can restrict to your frontend domain later
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize chatbot once
# bot = ChatBot()

# class Query(BaseModel):
#     question: str

# @app.post("/ask")
# async def ask_question(data: Query):
#     reply = bot.ask(data.question)
#     return {"response": reply}

# @app.get("/")
# def home():
#     return {"message": "VTU Chatbot API is running!"}



# # run th code ---->       uvicorn app:app --reload
