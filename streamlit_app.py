import streamlit as st
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
Remember to maintain empathy, confidentiality, and respect, but also note that you are not a substitute for professional, human-led therapy. 
Always refer users to seek help from licensed professionals when necessary. Keep the answers short and simple. <</SYS>>
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
        st.error("Error in model response")
        return "Error: " + post_model_outputs_response.status.description

    # Return the response
    return post_model_outputs_response.outputs[0].data.text.raw

# Streamlit UI
st.title('LLM Testing Sandbox')

user_input = st.text_input("Enter your text here", "")

if user_input:
    response = get_llm_response(user_input)
    st.text_area("Model Response", response, height=300)

