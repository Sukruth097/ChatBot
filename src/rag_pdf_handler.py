from dotenv import load_dotenv
from PyPDF2 import PdfReader
import PyPDF2 
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma,FAISS
# from langchain.vectorstores import FAISS
from langchain_openai import AzureChatOpenAI,AzureOpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import streamlit as st
import logging

load_dotenv()
os.environ["AZURE_OPENAI_API_KEY"] =  os.getenv("AZURE_OPENAI_API_KEY") 
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")

def get_text_chunks_with_metadata(pdf_docs):  
    chunks = []  
    metadatas = []  
    text = ""  
    for pdf in pdf_docs:  
        pdf_reader = PdfReader(pdf)  
        for page_number, page in enumerate(pdf_reader.pages):  
            try:  
                page_text = page.extract_text()  
                if page_text:  
                    text += page_text  
            except Exception as e:  
                logging.error(f"Error extracting text from page {page_number} of {pdf.name}: {e}")  
                continue  # Skip this page and continue with the next one  
  
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)  
    file_texts = text_splitter.split_text(text)  
    chunks.extend(file_texts)  
    file_metadatas = [{"source": f"{i}-{pdf.name}"} for i in range(len(file_texts))]  
    metadatas.extend(file_metadatas)  
    return chunks, metadatas  

# def get_text_chunks_with_metadata(pdf_docs):
#     chunks = []
#     metadatas = []
#     text = ""
#     for pdf in pdf_docs:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#     # for pdf in pdf_docs:
#     #     pdf_reader = PdfReader(pdf)
#     #     pdf_text = ""
#     #     for page in pdf_reader.pages:
#     #         pdf_text += page.extract_text()
            
#         # Split the text into chunks
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
#         file_texts = text_splitter.split_text(text)
#         chunks.extend(file_texts)

#         # Create a metadata for each chunk
#         file_metadatas = [{"source": f"{i}-{pdf.name}"} for i in range(len(file_texts))]
#         metadatas.extend(file_metadatas)
#     return chunks,metadatas


# def get_text_chunks(text):
#     text_splitter =  RecursiveCharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     chunks = text_splitter.split_text(text)
#     return chunks


def get_vectorstore(chunks,metadatas):
    embeddings = AzureOpenAIEmbeddings(azure_deployment="embedding_03large_model",openai_api_version="2024-06-01")
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings,metadatas=metadatas)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = AzureChatOpenAI(azure_deployment=st.session_state.deployment_name,  # or your deployment
    api_version="2024-02-01",  
    temperature=0)
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

