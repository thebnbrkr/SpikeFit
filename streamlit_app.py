import streamlit as st
from streamlit_chat import message
import requests
from datetime import datetime

# Streamlit UI with Chat
st.title('Virtual Psychologist and Dietitian Chat')

# Initialize the conversation with the template
initial_template = """[INST] <<SYS>> You are a virtual psychologist trained in Cognitive Behavioral Therapy (CBT) principles...
[Your detailed instructions here]
<<SYS>> [/INST]"""

# Function to get response from the API
def query_model(input_text):
    api_url = "https://api.deepinfra.com/v1/inference/meta-llama/Llama-2-70b-chat-hf"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['PAT']}"  # Using PAT from Streamlit's secrets
    }
    data_payload = {
        "input": input_text,
        "stream": False
    }
    response = requests.post(api_url, headers=headers, json=data_payload)
    return response.json()

def get_llm_response(user_input):
    if 'initialized' not in st.session_state:
        # Start the conversation with the initial template
        st.session_state.initialized = True
        query_model(initial_template)

    response = query_model(user_input)
    results = response.get('results', [])
    if results:
        return results[0].get('generated_text', '')
    return "No response from the model."

# Managing chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Enter your text here", key="input")

if st.button("Send"):
    if user_input:
        current_time = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({"message": user_input, "is_user": True, "timestamp": current_time})
        response = get_llm_response(user_input)
        st.session_state.chat_history.append({"message": response, "is_user": False, "timestamp": current_time})
        # Clear the input box after sending the message
        st.experimental_rerun()

# Display messages with unique keys and include timestamps
for i, chat in enumerate(st.session_state.chat_history):
    message(chat["message"], is_user=chat["is_user"], key=str(i))
    st.caption(chat["timestamp"])

# Optional: Add a container or padding at the bottom if you want to ensure the last message is not covered by the input box
st.container()
