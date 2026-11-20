import streamlit as st
import google.generativeai as genai
import requests
from hero_dict import superDict

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
api_token = st.secrets["SUPERHERO_API_TOKEN"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

st.title("SuperBot :robot:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


def get_chat_history_string():
    history_text = ""
    for msg in st.session_state.chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"
    return history_text


chatPrompt = st.chat_input("Enter your SuperQuestion!")

if chatPrompt:
    st.session_state.chat_history.append({"role": "user", "content": chatPrompt})
    with st.chat_message("user"):
        st.write(chatPrompt)

    placeholder = st.empty()
    with placeholder.container():
        st.write("Thinking of a good answer...")

    try:
        superhero = model.generate_content(
            f"You are an expert superhero analyst. Based on the following prompt: '{chatPrompt}', "
            f"I want you to, ONLY if applicable, pick a superhero from {superDict} needed to answer the question. "
            f"Return this superhero exactly as spelled in the dictionary, and return this as a string."
        )

        if superhero and superhero.text.strip():
            hero = superhero.text.strip().strip('"').strip("'")
            response = requests.get(f"[https://superheroapi.com/api/](https://superheroapi.com/api/){api_token}/search/{hero}")
            data = response.text

            prompt = (
                f"Based on this data: {data}, continue this chat history with the user: "
                f"{get_chat_history_string()}, and answer this prompt: {chatPrompt}. "
                f"Feel free to include interesting stats about the heroes you have data on. "
                f"Also, pretend the user does not know about the data I entered.\nAssistant:"
            )
            finalResponse = model.generate_content(prompt)
        else:
            finalResponse = model.generate_content(chatPrompt)

        placeholder.empty()
        with st.chat_message("assistant"):
            st.write(finalResponse.text)

        st.session_state.chat_history.append({"role": "assistant", "content": finalResponse.text})

    except Exception as e:
        placeholder.empty()
        with st.chat_message("assistant"):
            if "429" in str(e):
                st.markdown("Oops! You've hit your rate limit. Try again in a minute.")
            else:
                st.markdown("An error occurred. Try something else!")
