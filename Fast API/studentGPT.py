from googlesearch import search
import openai
import requests
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import speech_recognition as sr
from gtts import gTTS
import requests
import io
from PIL import Image
import requests
from secret_keys import *

openai.api_key= OPENAI_API_KEY

def generate_image_caption(filename):
    with open(filename,"rb") as f:
        data = f.read()
    response = requests.post(CAPTIONING_API_URL, headers=headers, data=data)
    return response.json()[0].get('generated_text')
    
def generate_the_image(prompt):
    #image_bytes = query({"inputs": prompt})
    image_bytes = requests.post(GENERATION_API_URL, headers=headers, json={"inputs":prompt}).content
    image = Image.open(io.BytesIO(image_bytes))
    image.save("generated_image.png")
    return image
    # return streaming response


def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(file_path)
    # Convert audio to WAV format
    audio = audio.set_frame_rate(44100)
    audio = audio.set_channels(1)
    wav_file_path = "recorded_audio.wav"
    audio.export(wav_file_path, format="wav")
    
    with sr.AudioFile(wav_file_path) as audio_file:
        audio_data = recognizer.record(audio_file)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    return None
    
def text_to_speech(text):
    save_path = "generated_audio.wav"
    tts = gTTS(text = text, lang="en")
    tts.save(save_path)
    return save_path
    
def list_references(answer):
    query = f"References for {answer}"
    references = list(search(query, num=5, stop=5))
    return references

def chatCompletion(prompt):
    engine = "gpt-3.5-turbo-instruct"
    response = openai.Completion.create(
        engine = engine,
        prompt = prompt,
        max_tokens = 1000,
        temperature = 0.9,
        stop = None
    )
    answer = response.choices[0].text.strip()
    return answer

