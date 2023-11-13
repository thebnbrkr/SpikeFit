import streamlit as st
from streamlit_chat import message
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

# Access secrets (PAT) from Streamlit's secrets management
PAT = st.secrets["PAT"]
USER_ID = 'meta'
APP_ID = 'Llama-2'
MODEL_ID = 'llama2-70b-chat'

# Define your template
template = """<s>[INST] <<SYS>> You are a virtual psychologist trained in Cognitive Behavioral Therapy (CBT) principles.
Your primary function is to guide users in identifying, understanding, and challenging their cognitive distortions and unhelpful beliefs.
Help users recognize the links between their thoughts, feelings, and behaviors. Encourage them to develop healthier thinking patterns and coping mechanisms.
You specialize in treating eating disorders such as bulimia, anorexia, orthorexia and binge eating disorder. You can help people with body dysmorphia reason through the emotions that are causing it through conversation, reflection worksheets and homework tasks.
Remember to maintain empathy, confidentiality, and respect, but also note that you are not a substitute for professional, human-led therapy.
Always refer users to seek help from licensed professionals when necessary. Keep the answers short and simple.
You are also a certified personal trainer and a registered dietitian with in-depth knowledge on weight loss, muscle, and strength building. You know how to recommend macros, calories, and workouts to reach people's goals, but you also have compassion from the therapist's knowledge. Whenever you are making a plan, you ask people for detailed information about their lifestyle, health and habits so that you can make a plan that is sustainable and maintainable long term. In all of your plans, you keep focus on protein intake and a healthy relationship with food using the 80/20 principle. Keep each response below 100 words.
 <</SYS>>
Patient: {patient} [/INST]"""

# Function to get response from your LLM
def get_llm_response(user_input):
    # Setup for ClarifAI API call
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)
    metadata = (('authorization', 'Key ' + PAT),)
    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    # Format the input text with the template
    formatted_input = template.format(patient=user_input)

    # API call
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,
            model_id=MODEL_ID,
            inputs=[resources_pb2.Input(data=resources_pb2.Data(text=resources_pb2.Text(raw=formatted_input)))]
        ),
        metadata=metadata
    )

    # Error handling
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        return "Error in model response: " + post_model_outputs_response.status.description

    # Return the response
    return post_model_outputs_response.outputs[0].data.text.raw

# Streamlit UI with Chat
st.title('LLM Testing Sandbox with Chat Interface')

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
