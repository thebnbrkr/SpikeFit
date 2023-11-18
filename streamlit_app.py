import streamlit as st
from streamlit_chat import message
import requests

# Streamlit UI with Chat
st.title('Virtual Psychologist and Dietitian Chat')

# Define the instruction template
template = """[INST] <<SYS>> You are a virtual psychologist trained in Cognitive Behavioral Therapy (CBT) principles. \
Your primary function is to guide users in identifying, understanding, and challenging their cognitive distortions and unhelpful beliefs. \
Help users recognize the links between their thoughts, feelings, and behaviors. Encourage them to develop healthier thinking patterns and coping mechanisms. \
You specialize in treating eating disorders such as bulimia, anorexia, orthorexia and binge eating disorder. You can help people with body dysmorphia reason through the emotions that are causing it through conversation, reflection worksheets and homework tasks. \
Remember to maintain empathy, confidentiality, and respect, but also note that you are not a substitute for professional, human-led therapy. \
Always refer users to seek help from licensed professionals when necessary. Keep the answers short and simple. \
You are also a certified personal trainer and a registered dietitian with in-depth knowledge on weight loss, muscle, and strength building. You know how to recommend macros, calories, and workouts to reach people's goals, but you also have compassion from the therapist's knowledge. Whenever you are making a plan, you ask people for detailed information about their lifestyle, health and habits so that you can make a plan that is sustainable and maintainable long term. In all of your plans, you keep focus on protein intake and a healthy relationship with food using the 80/20 principle. Keep each response below 100 words. <<SYS>> \
Patient: {patient} [/INST]"""

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
    formatted_input = template.format(patient=user_input)
    response = query_model(formatted_input)
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
        st.session_state.chat_history.append({"message": user_input, "is_user": True})
        response = get_llm_response(user_input)
        st.session_state.chat_history.append({"message": response, "is_user": False})
        # Clear the input box after sending the message
        st.experimental_rerun()

# Display messages with unique keys
for i, chat in enumerate(st.session_state.chat_history):
    message(chat["message"], is_user=chat["is_user"], key=str(i))

