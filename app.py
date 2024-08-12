import streamlit as st
from openai import OpenAI
import dotenv
import os
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import base64
from io import BytesIO
from src.openai import *
from src.rag_pdf_handler import *
from utils import *
from src.stt import *
import time
from htmlTemplate import *

dotenv.load_dotenv()
# os.environ["AZURE_OPENAI_API_KEY"] =  os.getenv("AZURE_OPENAI_API_KEY") 
# os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")


def main():
    st.set_page_config(
        page_title="Azure OpenAI Models ChatBot",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.write(css, unsafe_allow_html=True)
    st.html("""<h1 style="text-align: center; color: #6ca395;"> <i>Azure OpenAI Models ChatBot</i> </h1>""")
    default_azure_enpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    default_api_key = os.getenv("AZURE_OPENAI_API_KEY") 
    
    if "expander_open" not in st.session_state:  
        st.session_state.expander_open = True  
    if "model_params" not in st.session_state:
        st.session_state.model_params = None
    if "verification_status_code" not in st.session_state:
        st.session_state.verification_status_code = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "pdf_docs" not in st.session_state:
        st.session_state.pdf_docs = []
    if "process" not in st.session_state:
        st.session_state.process= None
    
    with st.sidebar:
        with st.popover("🔐 Azure OpenAI Credentials"):
            azure_llm_endpoint = st.text_input("Enter your Azure OpenAI endpoint (https://oai.azure.com/portal/)", value= default_azure_enpoint)
            open_api_key = st.text_input("Enter your Azure OpenAI API key ", value=default_api_key, type="password")    
            verify= st.button("Verify the Credentials")
            if verify:
                with st.spinner('Processing...'):
                 st.session_state.verification_status_code,_ = verify_azure_openai_credentials(azure_llm_endpoint,open_api_key)

    if default_api_key == "" or default_api_key is None :
        st.write("#")
        st.warning("⬅️ Please enter your Azure OpenAI API Endpoint and Key to continue...")
    else: # st.session_state.verification_status_code == 200 or st.session_state.verification_status_code == 202:
        # st.write("Successfully established Azure OpenAI connection")
                
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
            
        if "deployment_list" not in st.session_state:
            st.session_state.deployment_list = load_deployment_names()

        if "deployment_name" not in st.session_state:
            st.session_state.deployment_name = st.session_state.deployment_list[0]
            
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                for content in message['content']:
                    if content['type'] == "text":
                        st.write(content['text'])
                    elif content["type"] == "image_url":
                        st.image(content["image_url"]["url"]) 
         
                      
        with st.sidebar:
            model = st.selectbox("Select a model:", [
                    # "Pick any model from below list",
                    "gpt-4o", 
                    "gpt-4-turbo", 
                    "gpt-3.5-turbo-16k", 
                    "gpt-4", 
                    "gpt-4-32k",
                ], index=None) 
                  
            if model:
                with st.expander("⚙️ Model parameters", expanded=st.session_state.expander_open):
                    selected_deployment = st.selectbox(
                        "Select an option or add a new one:",
                        st.session_state.deployment_list,
                        index=st.session_state.deployment_list.index(st.session_state.deployment_name) if st.session_state.deployment_name in st.session_state.deployment_list else 0
                    )
                    
                    if selected_deployment == "Add your deployment_name":
                        new_deployment_name = st.text_input("Please enter the deployment name", key="new_deployment_name")
                        if new_deployment_name:
                            if new_deployment_name not in st.session_state.deployment_list:
                                st.session_state.deployment_list.insert(-1, new_deployment_name)
                                st.session_state.deployment_name = new_deployment_name
                                save_deployment_names(st.session_state.deployment_list)
                            else:
                                st.error("Deployment name already exists. Please choose a different one.")
                    else:
                        # Update session state with the selected deployment name
                        st.session_state.deployment_name = selected_deployment
                    
                    # Other model parameters
                    model_temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
                    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
                    max_tokens = st.number_input("Enter the max tokens to be generated for response", value=600, step=10)
                    
                    if st.button("Submit Parameters to the Model"):
                        st.session_state.expander_open = False
                        model_params = {
                            "deployment_name": st.session_state.deployment_name,
                            "temperature": model_temp,
                            "top_p": top_p,
                            "max_tokens": max_tokens
                        }
                        st.session_state.model_params = model_params
                        st.write("Parameters Submitted Successfully")
                        time.sleep(1)
                        st.rerun()
    
                    # print(f"The final deployment name: {st.session_state.deployment_name}")
                    print(f"The model parameters: {st.session_state.model_params}")
                # with st.popover("⚙️ Model parameters"):
                # with st.expander("⚙️ Model parameters", expanded=st.session_state.expander_open):
                #     st.session_state.deployment_name = st.selectbox("Select an option or add a new one:",
                #     st.session_state.deployment_list,
                #     index=st.session_state.deployment_list.index(st.session_state.deployment_name) if st.session_state.deployment_name in st.session_state.deployment_list else 0)
                #     print(st.session_state.deployment_name)
                #     if st.session_state.deployment_name == "Add your deployment_name":
                #         new_deployment_name= st.text_input("Please enter the deploment name", key="new_deployment_name")
                #         if new_deployment_name:
                #             if new_deployment_name not in st.session_state.deployment_list:
                #                 st.session_state.deployment_list.append(new_deployment_name)
                #                 st.session_state.deployment_name = new_deployment_name
                #             else:
                #                 st.error("Deployment name already exists. Please choose a different one.")
                #     print(f"New Deployment name is {st.session_state.deployment_name}")
                #     # deployment_name = st.text_input("Please enter the deploment name", value="llm-gpt40-model")
                #     model_temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
                #     top_p = st.slider("Top P",min_value=0.0,max_value=1.0, value=0.0, step=0.1)
                #     max_tokens = st.number_input("Enter the max tokens to be generated for response",value=600,step=10)
                #     if st.button("Submit Parameters to the Model"):  
                #         st.session_state.expander_open = False  
                #         model_params = {  
                #             "deployment_name": st.session_state.deployment_name,  
                #             "temperature": model_temp,  
                #             "top_p": top_p,  
                #             "max_tokens": max_tokens  
                #         }  
                #         st.session_state.model_params = model_params
                #         print(st.session_state.model_params)
                #         st.write("Parameters Submitted Successfully")
                #         print("Parameters Submitted Successfully")
                #         time.sleep(1.05)
                #         st.rerun() 
             
                #     print(f"The final deployment name : {st.session_state.deployment_name}")    
            audio_response = st.toggle("Audio Response",value=False)
            # if audio_response:
            #     cols = st.columns(2)
            #     with cols[0]:
            #         model = st.selectbox("Select a model",["tts-1", "tts-1-hd"],index=None)
            #     with cols[1]:
            #         voice = st.selectbox("Select a voice ",["alloy", "echo", "fable", "onyx", "nova", "shimmer"], index=None)
            
            def reset_conversation():
                if "messages" in st.session_state and len(st.session_state.messages) > 0:
                    st.session_state.pop("messages", None)

            st.button(
                "🗑️ Reset conversation", 
                on_click=reset_conversation,
            )

            st.divider() 
            
            if model:
                st.subheader("RAG")
                st.session_state.pdf_docs = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
                # st.write(f"Uploaded {len(st.session_state.pdf_docs)} pdf files: {[file.name for file in st.session_state.pdf_docs]}")
                st.session_state.process= st.button("Process")
                if st.session_state.process:
                    with st.spinner("Processing"):
                        
                        chuncks, metadata = get_text_chunks_with_metadata(st.session_state.pdf_docs)
                        
                        # # get the text chunks
                        # text_chunks = get_text_chunks(raw_text)

                        # create vector store
                        vectorstore = get_vectorstore(chuncks,metadata)

                        # create conversation chain
                        st.session_state.conversation = get_conversation_chain(
                            vectorstore)
                        st.write("Successfully created conversation chain for the uploaded files")
                        
                        
                        
                        
        # if st.session_state.pdf_docs:
        #     st.write(f"Uploaded {len(st.session_state.pdf_docs)} pdf files: {[file.name for file in st.session_state.pdf_docs]}")   
        # else:
        #     pass
            st.divider()
            
                
            def add_image_to_messages():
                if st.session_state.uploaded_img or st.session_state.camera_img:
                    img_type = st.session_state.uploaded_img.type if st.session_state.uploaded_img else "image/jpeg"
                    raw_img = Image.open(st.session_state.uploaded_img or st.session_state.camera_img)
                    img = get_image_base64(raw_img)
                    st.session_state.messages.append(
                        {
                            "role": "user", 
                            "content": [{
                                "type": "image_url",
                                "image_url": {"url": f"data:{img_type};base64,{img}"}
                            }]
                        }
                    )
            if model in ["gpt-4o", "gpt-4-turbo"]:
                st.write("### **🖼️ Add an image:**")
                cols_img = st.columns(2)
                with cols_img[0]:
                    with st.popover("📁 Upload"):
                        st.file_uploader(
                            "Upload an image", 
                            type=["png", "jpg", "jpeg"], 
                            accept_multiple_files=False,
                            key="uploaded_img",
                            on_change=add_image_to_messages,
                        )
                with cols_img[1]:                    
                    with st.popover("📸 Camera"):
                        activate_camera = st.checkbox("Activate camera")
                        if activate_camera:
                            st.camera_input(
                                "Take a picture", 
                                key="camera_img",
                                on_change=add_image_to_messages,
                            )
            
            st.divider()
            
            audio_prompt = None
            if "prev_speech_hash" not in st.session_state:
                st.session_state.prev_speech_hash = None
            
            if model:  
                speech_input = audio_recorder("Press to talk:", icon_size="3x", neutral_color="#6ca395" )
                if speech_input and st.session_state.prev_speech_hash != hash(speech_input):
                    st.session_state.prev_speech_hash = hash(speech_input)
                    # client = azure_client_connection()
                    # transcript = client.audio.transcriptions.create(
                    #     model="whisper_stt_model", 
                    #     file=("audio.wav", speech_input),
                    # )
        
                    # audio_prompt = transcript.text
                    audio_prompt = speech_to_text()
                    print(audio_prompt)
        if "total_response" not in st.session_state:
            st.session_state.total_response = ""  
            
            st.divider()  
                
        if model:
            if prompt :=st.chat_input("Hello , Ask anything you need answer for...") or audio_prompt:     
                st.session_state.messages.append(
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": prompt or audio_prompt,
                            }
                        ]
                    }
                )
                

                # with st.chat_message('user'):
                #     st.markdown(prompt or audio_prompt)
                
                if st.session_state.pdf_docs:
                    st.write(f"Uploaded {len(st.session_state.pdf_docs)} pdf files: {[file.name for file in st.session_state.pdf_docs]}")
             
                    response = st.session_state.conversation({'question': prompt})
                    st.session_state.messages.append(  
                        {  
                            "role": "assistant",  
                            "content": [  
                                {  
                                    "type": "text",  
                                    "text": response['chat_history'][-1].content,  
                                }  
                            ]  
                        }  
                    ) 
                    display_chat()
                    # with st.chat_message('assistant'):
                    #     st.session_state.chat_history = response['chat_history']

                    #     for i, message in enumerate(st.session_state.chat_history):
                    #         if i % 2 == 0:
                    #             st.write(user_template.replace(
                    #                 "{{MSG}}", message.content), unsafe_allow_html=True)
                    #         else:
                    #             st.write(bot_template.replace(
                    #                 "{{MSG}}", message.content), unsafe_allow_html=True)
                    # st.write(response)
                else:
                    with st.chat_message('user'):
                        st.markdown(prompt or audio_prompt)
                    client = azure_client_connection() 
                    with st.chat_message('assistant'):  
                        st.write_stream(stream_llm_response(client=client, model_params=st.session_state.model_params))  
               
                
                if audio_response:  
                    audio_r = text_to_speech(st.session_state.messages[-1]["content"][0]["text"])  
                    audio_base64 = base64.b64encode(audio_r).decode('utf-8')  
                    audio_html = f"""  
                    <audio controls>  
                        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">  
                    </audio>  
                    """  
                    st.markdown(audio_html, unsafe_allow_html=True)
                # else:
            #     st.write_stream(
            #         stream_llm_response(client=client, model_params=st.session_state.model_params)
            #     )
               
                    
                        
                         
if __name__ == "__main__":
    main()