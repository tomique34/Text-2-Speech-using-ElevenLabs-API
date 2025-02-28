# Import the required libraries
from pathlib import Path
import requests
import os
import time
import warnings
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

# Suppress DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set page title, favicon, and description
st.set_page_config(
    page_title='Text-2-Speech Generator using ElevenLabs API',
    page_icon='./img/announcing.png',
    layout='centered',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Text 2 Speech Converter using *ElevenLabs API*. \n\n This app is created by [Tomique34](https://www.linkedin.com/in/tomasvince/)."
    }
)

# Streamlit app interface
st.title('Text to Speech Generator using ElevenLabs API')

# Request the ElevenLabs API key from the user via the sidebar
elevenlabs_api_key = st.sidebar.text_input("Enter your ElevenLabs API key:", type="password")

# Add a confirmation button below the API key input
key_entered = st.sidebar.button('Register API Key')

if key_entered:
    # This block only runs when the button is pressed
    if elevenlabs_api_key:
        # Perform actions that require the API key
        st.sidebar.success("API key has been registered successfully.")
        st.session_state['elevenlabs_api_key'] = elevenlabs_api_key
    else:
        st.sidebar.error("Please enter an valid Elevenlabs API key to proceed..")
        # Prevent the rest of the code from executing
        st.stop()

# Now we check if the API key is in the session state before making any API calls
if 'elevenlabs_api_key' in st.session_state and st.session_state['elevenlabs_api_key']:
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=st.session_state['elevenlabs_api_key'])
        
        # Test API connection by fetching voices
        try:
            # Proceed with API calls and other operations that require the API key
            # Initialize an empty list to hold the voice names for Streamlit dropdown menu options
            voice_names = []

            # List all available Elevenlabs voices and add their names to the dropdown options
            supported_voices = client.voices.get_all()
            for voice in supported_voices.voices:
                voice_names.append(voice.name)

            # Dropdown menu for voice selection
            selected_voice = st.selectbox("Choose a voice for speech generation:", voice_names)

            # Text area for user input
            user_input_text = st.text_area("Enter the text you want to convert to speech:", height=150)

            # Submit button to convert the text to speech
            submit = st.button('Convert to Speech')

            if submit and user_input_text:
                # Process the conversion
                try:
                    # Get the current date and time for filename uniqueness
                    now = datetime.now()
                    date_string = now.strftime("%Y-%m-%d_%H-%M")
                    
                    # Create directory if it doesn't exist
                    speech_file_directory = Path(__file__).parent / "audio-outputs"
                    speech_file_directory.mkdir(parents=True, exist_ok=True)
                    
                    speech_file_path = speech_file_directory / f"speech-{date_string}.mp3"

                    # Generate the speech audio using Elevenlabs API from the provided text
                    response = client.generate(
                        text=user_input_text,
                        voice=selected_voice,
                        model="eleven_multilingual_v2"
                    )

                    # Save the response to a file
                    with open(speech_file_path, 'wb') as out_file:
                        for chunk in response:
                            out_file.write(chunk)

                    st.success("The audio file has been created successfully.")

                    # Provide a link for the user to download the MP3 file
                    with open(speech_file_path, 'rb') as audio_file:
                        audio_data = audio_file.read()

                    st.download_button(
                        label="Download Speech File",
                        data=audio_data,
                        file_name=speech_file_path.name,
                        mime="audio/mp3"
                    )
                    
                    # Display an audio player option to listen to the generated speech
                    st.audio(audio_data, format='audio/mp3', start_time=0)

                except Exception as e:
                    st.error(f"An error occurred during audio generation: {str(e)}")
            elif submit:
                st.error("Please enter some text to convert to speech.")

        except Exception as e:
            # Handle exceptions that may occur during the API calls to fetch voices
            st.error(f"Error fetching voices. Please check your API key: {e}")
            # Clear the invalid API key from session state
            st.session_state.pop('elevenlabs_api_key', None)
            st.sidebar.error("API key validation failed. Please enter a valid key.")
    
    except ImportError as e:
        st.error(f"Error importing ElevenLabs: {e}. Please ensure 'elevenlabs' is installed.")
else:
    # Prompt the user to enter the API key
    st.info("Please enter your ElevenLabs API key on left side first to proceed.")
    # Prevent the rest of the code from executing
    st.stop()

# Footer
footer = """
    <style>
    .reportview-container .main footer {visibility: hidden;}
    </style>
    <div style="position: fixed; bottom: 0; width: 100%; text-align: left; color: white; padding: 10px;">
        <p>Crafted by Tomique</p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)

# Function to clean up old audio files
def cleanup_files(directory, max_age=600):
    """
    Remove files in the specified directory that are older than max_age seconds.
    """
    if not os.path.exists(directory):
        return  # Exit if the directory doesn't exist
    for filename in os.listdir(directory):
        file_path = Path(directory) / filename
        if file_path.is_file() and file_path.stat().st_mtime < time.time() - max_age:
            try:
                file_path.unlink()
                print(f"Deleted old file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

# Call this function at the end of your Streamlit script to clean up old audio files
cleanup_files('./audio-outputs/', max_age=600)
