import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import threading

# Configure the API key directly
genai.configure(api_key="YOUR_API_KEY")

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

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

def speak_text(text):
    def run_tts():
        tts_engine.say(text)
        tts_engine.runAndWait()
    
    tts_thread = threading.Thread(target=run_tts)
    tts_thread.start()

# Streamlit app configuration
st.set_page_config(page_title="eleAi")

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

st.markdown("<h1>Welcome to eleAi</h1>", unsafe_allow_html=True)

mode = st.radio("Select Input Mode:", options=["Speak", "Type"], index=1)

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
                        if hasattr(chunk, 'text') and chunk.text:
                            st.write(chunk.text)
                            full_response += chunk.text
                        else:
                            st.warning("No valid response received.")

                    if full_response:
                        speak_text(full_response)

            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your voice.")
            except sr.RequestError:
                st.error("Could not request results; please check your internet connection.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

elif mode == "Type":
    input_text = st.text_input("Type your question and press Enter:", key="input")

    if input_text:
        response = get_gemini_response(input_text)
        if response:
            st.subheader("Response:")
            full_response = ""
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    st.write(chunk.text)
                    full_response += chunk.text
                else:
                    st.warning("No valid response received.")

        # Speak the response if present
        if full_response:
            speak_text(full_response)
