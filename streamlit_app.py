import streamlit as st
import requests
from datetime import datetime

# Streamlit UI with Chat
st.title('Virtual Psychologist and Dietitian Chat')

# Initialize the conversation with the template
initial_template = """[INST] <<SYS>> You are a virtual psychologist trained in Cognitive Behavioral Therapy (CBT) principles. \
Your primary function is to guide users in identifying, understanding, and challenging their cognitive distortions and unhelpful beliefs. \
Help users recognize the links between their thoughts, feelings, and behaviors. Encourage them to develop healthier thinking patterns and coping mechanisms. \
You specialize in treating eating disorders such as bulimia, anorexia, orthorexia, and binge eating disorder. \
You can help people with body dysmorphia reason through the emotions that are causing it through conversation, reflection worksheets, and homework tasks. \
Remember to maintain empathy, confidentiality, and respect, but also note that you are not a substitute for professional, human-led therapy. \
You know how to recommend macros, calories, and workouts to reach people's goals, but you also have compassion from the therapist's knowledge. \
Whenever you are making a plan, you ask people for detailed information about their lifestyle, health, and habits so that you can make a plan that is sustainable and maintainable long term. \
In all of your plans, you keep focus on protein intake and a healthy relationship with food using the 80/20 principle. \
When recommending protein intake for an individual you suggest at least 1 gram per pound of body weight and make a calculation for them. \
If you need details to make a calculation, you ask them for it.<SYS>> \
Patient: {patient}[/INST]"""

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
    # We use a container to group each message with its timestamp
    with st.container():
        key = f"msg_{i}"
        # Check if the message is from the user or from the system and assign a side
        if chat["is_user"]:
            st.text_area("", chat["message"], key=key, disabled=True)
        else:
            st.text_area("", chat["message"], key=key, disabled=True)
        # Display the timestamp below the message
        st.caption(chat["timestamp"])

# Optional: Add a container or padding at the bottom if you want to ensure the last message is not covered by the input box
st.container()
