import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import threading
from gtts import gTTS
import os

# Streamlit app configuration (Move this to the very top)
st.set_page_config(page_title="eleAi")

# Configure the API key directly
genai.configure(api_key="AIzaSyBN9ZlpzLLoHklPYo7d_7y7Uw9UW1wlE9E")

# Function to load the Gemini Pro model and get a response
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    try:
        response = chat.send_message(question, stream=True)
        return response
    except ValueError as e:
        st.error(f"Error in generating response: {str(e)}")
        return None

# Initialize Text-to-Speech engine (for fallback)
tts_engine = None
try:
    # Attempt to initialize with the sapi5 driver on Windows
    tts_engine = pyttsx3.init(driverName='sapi5')  # For Windows, uses SAPI5
    tts_engine.setProperty('rate', 150)  # Adjust the speaking rate if necessary
except RuntimeError as e:
    st.warning(f"pyttsx3 failed to initialize: {e}, using gTTS instead.")
    tts_engine = None

def speak_text(text):
    if tts_engine:
        # Using pyttsx3 if it's initialized
        def run_tts():
            tts_engine.say(text)
            tts_engine.runAndWait()

        # Run TTS in a separate thread to prevent blocking the main thread
        tts_thread = threading.Thread(target=run_tts)
        tts_thread.start()
    else:
        # Fallback to gTTS if pyttsx3 is not available
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        os.system("mpg321 response.mp3")  # Make sure mpg321 is installed to play audio

# CSS for positioning the logo on the top left
st.markdown("""
    <style>
    .top-left-logo {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 50px;
        height: auto;
    }
    h1 {
        text-align: center;
        color: cyan;
        margin-top: 0;
    }
    .stTextInput, .stButton, .stMarkdown {
        font-size: 18px;
    }
    .jarvis-container {
        border: 2px solid cyan;
        border-radius: 10px;
        padding: 20px;
        background-color: #1e1e1e;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Display team logo in the top-left corner
st.sidebar.image("teamlogo.png", use_column_width=True) 

# Streamlit app title
st.markdown("<h1>Welcome to eleAi</h1>", unsafe_allow_html=True)

# Options for input mode: Text or Voice
mode = st.radio("Select Input Mode:", options=["Speak", "Type"], index=1)

# Voice input handler
if mode == "Speak":
    if st.button("Record Your Question"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                input_text = recognizer.recognize_google(audio)
                st.success(f"You said: {input_text}")

                response = get_gemini_response(input_text)
                if response:
                    st.subheader("Response:")
                    full_response = ""

                    for chunk in response:
                        # Ensure the chunk has the attribute 'text' and handle any error in content access
                        if hasattr(chunk, 'text') and chunk.text:
                            st.write(chunk.text)
                            full_response += chunk.text
                        else:
                            st.warning("No valid response received. The model might have detected copyrighted content.")

                    # Speak the response if mode is "Speak"
                    if full_response:
                        speak_text(full_response)

            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your voice.")
            except sr.RequestError:
                st.error("Could not request results; please check your internet connection.")

# Text input handler
elif mode == "Type":
    input_text = st.text_input("Type your question and press Enter:", key="input", on_change=lambda: st.session_state.update({'response_trigger': True}))

    if st.session_state.get('response_trigger', False) and input_text:
        st.session_state['response_trigger'] = False  # Reset the trigger
        response = get_gemini_response(input_text)
        if response:
            st.subheader("Response:")
            full_response = ""
            for chunk in response:
                # Ensure the chunk has the attribute 'text' and handle any error in content access
                if hasattr(chunk, 'text') and chunk.text:
                    st.write(chunk.text)
                    full_response += chunk.text
                else:
                    st.warning("No valid response received. The model might have detected copyrighted content.")
