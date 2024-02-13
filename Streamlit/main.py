import streamlit as st
import openai
from secret_key import OPENAI_API_KEY
from googlesearch import search
from PIL import Image
import requests
from io import BytesIO
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import speech_recognition as sr
from gtts import gTTS


openai.api_key = OPENAI_API_KEY

def get_references(answer):
    print("Looking for response references")
    query = f"References for {answer}"
    references = list(search(query, num=5, stop=5))
    print("Fetched the references")
    return references

def get_voice_input():
    print("Start speaking-")
    duration = 5 # seconds
    sample_rate= 44100
    channels = 1
    # Record audio from the microphone
    recording = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=channels, dtype=np.int16)
    sd.wait()

    # Convert the NumPy array to an AudioSegment
    audio_segment = AudioSegment(
        recording.tobytes(),
        frame_rate=sample_rate,
        sample_width=recording.dtype.itemsize,
        channels=channels
    )

    # Save the audio to an MP3 file
    file_path = "recorded_audio.wav"
    audio_segment.export(file_path, format="mp3")
    print("Audio file saved")
    
def convert_audio_to_text(file_path):
    print("Loading audio file:")
    recognizer = sr.Recognizer()
    
    audio = AudioSegment.from_file(file_path)
    # Play audio
    #play(audio)
    
    # Convert to WAV format
    audio = audio.set_frame_rate(44100)  # Adjust the frame rate if needed
    audio = audio.set_channels(1)  # Convert to mono if needed
    # Save as WAV file
    wav_file_path = "recorded_audio.wav"
    audio.export(wav_file_path, format="wav")
    
    with sr.AudioFile(wav_file_path) as audio_file:
        audio_data = recognizer.record(audio_file)
        
        try:
            text = recognizer.recognize_google(audio_data)
            print("Audio converted to text:- ", text)
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    return None
    

def convert_text_to_speech(text):
    save_path= "generated_audio.wav"
    tts= gTTS(text=text, lang="en")
    tts.save(save_path)
    
def generate_response(prompt, task_type):
    print("Prompt received:-", prompt)
    engine = "gpt-3.5-turbo-instruct"
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=500,  
        temperature=0.7,  
        stop=None 
    )
    answer = response.choices[0].text.strip()
    print("Answer generated")

    return answer


def main():
    st.title("Career Companion:- Student GPT")

    task_type = st.selectbox("Select Task Type", ["Question Answering", "Image generation", "Video generation"])
    if task_type=="Question Answering":
        # User input options
        input_option = st.radio("Select input method:", ["Text", "Voice"])
        if input_option == "Text":
            user_input = st.text_area("Ask a question:")
        elif input_option == "Voice":
            get_voice_input()
            st.write("You spoke:-")
            st.audio("recorded_audio.wav", start_time=0)
            user_input=convert_audio_to_text("recorded_audio.wav")

    elif task_type=="Image generation" or task_type=="Video generation":
        st.write("Will be developed soon")

    if st.button("Generate"):
        response= generate_response(user_input, task_type)
        convert_text_to_speech(response)
        st.subheader("Answer:")
        st.write(response)
        st.audio("generated_audio.wav", start_time=0)
        
        references = get_references(response)
        st.subheader("References:")
        for ref in references:
            st.write(ref)

if __name__ == "__main__":
    main()
