import os
from dotenv import load_dotenv   
import azure.cognitiveservices.speech as speechsdk

load_dotenv()  

def text_to_speech(azure_llm_response):
    
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('AZURE_SPEECH_API_KEY'), region=os.environ.get('AZURE_SPEECH_REGION'))  
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)  
    # The neural multilingual voice can speak different languages based on the input text.  
    speech_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'  
      
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)  
    speech_synthesis_result = speech_synthesizer.speak_text_async(azure_llm_response).get()
    # speech_synthesizer.synthesis_completed.__context_ptr
    
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:  
        audio_data = speech_synthesis_result.audio_data  
        return audio_data  
    else:  
        print(f"Error synthesizing speech: {speech_synthesis_result.error_details}")  
        return None  
    #

def speech_to_text(audio_type="microphone", file=None):
    
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('AZURE_SPEECH_API_KEY'), region=os.environ.get('AZURE_SPEECH_REGION'))
    speech_config.speech_recognition_language="en-US"

    print("Speaking into your microphone.")
    if audio_type == "microphone":
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        speech_recognition_result = speech_recognizer.recognize_once_async().get()
    else:
        audio_config = speechsdk.audio.AudioConfig(filename=file)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        speech_recognition_result = speech_recognizer.recognize_once_async().get()
        
    return speech_recognition_result.text
        

   
            
            



# Example usage
if __name__ == "__main__":
    azure_llm_response = "Hello, this is a test message."
    text_to_speech(azure_llm_response)
    # result=speech_to_text()
    # print(result)
      
