import streamlit as st
from openai import AzureOpenAI
import dotenv
import os
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import base64
from io import BytesIO

dotenv.load_dotenv()
# print(os.getenv('AZURE_OPENAI_ENDPOINT'))


def azure_client_connection():
    try:
        client = AzureOpenAI(
                    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
                    api_version="2024-02-01"
                    )
        return client
    except Exception as e:
        raise e

def stream_llm_response(client,model_params):
    
    response_message = ""  
    response = client.chat.completions.create(  
        model=model_params.get("deployment_name", "llm-gpt40-model"),  
        messages=st.session_state.messages,  
        temperature=model_params.get("temperature", 0.3),  
        max_tokens=model_params.get("max_tokens", 4096),  
        stream=True  
    )  
      
    for chunk in response:  
        if chunk.choices and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):  
            chunk_text = chunk.choices[0].delta.content or ""  
            response_message += chunk_text  
            yield chunk_text  

    st.session_state.messages.append({
        "role": "assistant", 
        "content": [
            {
                "type": "text",
                "text": response_message,
            }
        ]})
    

    