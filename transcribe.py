import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os 
import json
import requests
from pathlib import Path
from typing import Dict, Any

class AzureOpenAIChat:
    def __init__(self):
        self.API_ENDPOINT = st.secrets.get("AZURE_OPENAI_API_ENDPOINT", "")
        self.API_KEY = st.secrets.get("AZURE_OPENAI_API_KEY", "")

    def generate_response(self, query: str)->Dict[str, Any]:
    #def generate_response(self, query: str, max_tokens: int = 2000)->Dict[str, Any]:
        """Generate response from Azure OpenAI"""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.API_KEY,
        }

        data = {
            "messages": [{"role": "user", "content": query}],
            #"max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        
        }
        try:
            response = requests.post(self.API_ENDPOINT, headers=headers, json=data)
            response.raise_for_status()  # Automatically raises an error for HTTP issues
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error: API request failed.", str(e))
        return {} 
def transcribe_audio(video_url):
    """Transcribe audio using Azure's Whisper API."""
    try:
        # Get credentials from streamlit secrets
        api_key = st.secrets["whisper"]["api_key"]
        endpoint_url = st.secrets["whisper"]["endpoint_url"]
        yt = YouTube(video_url, on_progress_callback=on_progress)
        ys = yt.streams.get_audio_only()
        audio_file=ys.download()

        if audio_file:
            file_name = os.path.basename(audio_file)
            st.write(file_name)
        
# Prepare and send the request
            with open(file_name, 'rb') as audio:
                response = requests.post(
                    endpoint_url,
                    headers={"api-key": api_key},
                    files={"file": (file_name, audio, 'audio/wav')},
                    timeout=80000
            )
        
            response.raise_for_status()
            return response.json().get('text')
    except Exception as e:
        print(f"Error transcribing {file_name}: {str(e)}")
        return None
def main():
    st.title("YouTube Video Summarizer")
    st.write("Enter a YouTube video link, and we'll summarize its content for you!")
    video_url = st.text_input("Paste the YouTube link here:")
    if st.button("Click Me"):
        text=transcribe_audio(video_url)
        #st.write(text)
        prompt = f"""
           Use the {text} and get the top 5 key points from this video in a short sumary
            """
        chat_client = AzureOpenAIChat()
        response = chat_client.generate_response(prompt)
        video_content = response["choices"][0]["message"]["content"]
        video_content = video_content.replace("```json", "").replace("```", "").strip()
        st.write(video_content)
        st.write("done")

    #if st.button("Summarize Video") and video_url:
     #   st.write("Processing video... (Backend logic needed)")

if __name__ == "__main__":
    main()