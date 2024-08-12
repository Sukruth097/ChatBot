import os
import requests
import streamlit as st
from io import BytesIO
import base64
from gtts import gTTS
import io
import streamlit as st
from htmlTemplate import *


def verify_azure_connection(default_azure_enpoint,default_api_key):
    with st.sidebar:
        with st.popover("🔐 Azure OpenAI Credentials"):
            azure_llm_endpoint = st.text_input("Enter your Azure OpenAI endpoint (https://oai.azure.com/portal/)", value= default_azure_enpoint)
            open_api_key = st.text_input("Enter your Azure OpenAI API key ", value=default_api_key, type="password")    
            verify= st.button("Verify the Credentials")
            if verify:
                with st.spinner('Processing...'):
                 verification_code,_ = verify_azure_openai_credentials(azure_llm_endpoint,open_api_key)
    return verification_code

def verify_azure_openai_credentials(endpoint,api_key):
   
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }
 
    url = f"{endpoint}openai/models?api-version=2024-06-01"
 
    try:
        # response = requests.post(url, headers=headers, json=payload)
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        result = response.status_code
        if result == 200 or 202:
            return response.status_code , st.success(f"{response.status_code}--Verified- Successfully established Azure OpenAI connection")
    except requests.RequestException as e:
        return st.error(f"Failed to make the request. Error: {e}")
    
    
def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()

    return base64.b64encode(img_byte).decode('utf-8')

def generate_audio_data(text):
    """
    Converts the given text to speech and returns the audio data in bytes.

    Parameters:
    text (str): The text to be converted to speech.

    Returns:
    bytes: The audio data in bytes format.
    """
    # Convert text to speech
    tts = gTTS(text, lang='en')
    
    # Save the audio to a bytes buffer
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    
    # Get the byte data from the buffer
    audio_buffer.seek(0)
    audio_data = audio_buffer.read()
    
    return audio_data

import json
import os

DEPLOYMENT_FILE_PATH = "deployments.json"


def load_deployment_names():
    if os.path.exists(DEPLOYMENT_FILE_PATH) and os.path.getsize(DEPLOYMENT_FILE_PATH) > 0:
        with open(DEPLOYMENT_FILE_PATH, "r") as file:
            return json.load(file)
    else:
        return ["llm-gpt40-model","embedding_03large_model","whisper_stt_model","Add your deployment_name"]  # Default values

def save_deployment_names(deployment_list):
    with open(DEPLOYMENT_FILE_PATH, "w") as file:
        json.dump(deployment_list, file)
        
def display_chat():  
    for message in st.session_state.messages:  
        if message["role"] == "user":  
            st.markdown(user_template.replace("{{MSG}}", message["content"][0]["text"]), unsafe_allow_html=True)  
        else:  
            st.markdown(bot_template.replace("{{MSG}}", message["content"][0]["text"]), unsafe_allow_html=True) 




# def save_new_option(option):
#     # Add the new option to the list of options
#     st.session_state.options.append(option)
#     # Optionally save this to a file or database here

# # Display the selectbox with existing options and an option to add a new one
# option = st.selectbox("Select an option or add a new one:", st.session_state.options + ["Add a new option..."])

# # If the user selects to add a new option
# if option == "Add a new option...":
#     new_option = st.text_input("Enter the new option:")
#     if new_option:
#         save_new_option(new_option)
#         st.success(f"'{new_option}' has been added.")
# else:
#     st.write(f"You selected: {option}")

    
    
 
# Example usage
# if __name__ == "__main__":
#     API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
#     ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  
 
#     verification_result = verify_azure_openai_credentials(endpoint=ENDPOINT,api_key=API_KEY)
#     print(verification_result)