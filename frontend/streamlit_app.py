import streamlit as st
import requests

BACKEND_URL = "http://rag-chatbot-service:8000"

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 RAG Chatbot")

st.markdown(
    "Ask questions from your uploaded documents"
)

question = st.text_input(
    "Enter your question"
)

if st.button("Ask"):

    if question:

        try:

            response = requests.post(
                f"{BACKEND_URL}/ask",
                json={
                    "question": question
                }
            )

            if response.status_code == 200:

                result = response.json()

                st.success("Answer")

                st.write(
                    result.get(
                        "answer",
                        "No answer returned"
                    )
                )

            else:

                st.error(
                    f"API Error: {response.status_code}"
                )

        except Exception as e:

            st.error(str(e))
