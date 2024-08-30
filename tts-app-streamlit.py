# Description: This is a simple Python script that uses the ElevenLABS API to convert text to speech and save the audio file to disk.

# Import the required libraries
from pathlib import Path
import requests
import os
import time
import warnings
from dotenv import load_dotenv
from datetime import datetime
from elevenlabs.client import ElevenLabs
import streamlit as st
import pydantic as pydantic

# Suppress DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# To handle warnings related to no supported SSL module
import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Suppress specific warnings
#from pydantic._internal._config import UserWarning as PydanticUserWarning
#from pydantic._internal._fields import UserWarning as PydanticFieldWarning
#warnings.filterwarnings("ignore", category=PydanticUserWarning)
#warnings.filterwarnings("ignore", category=PydanticFieldWarning)
# End area, where warning messages are handled/ignored

# Set page title, favicon, and description
st.set_page_config(
    page_title='Text-2-Speech Generator using ElevenLabs API',      # Your app title
    page_icon='./img/announcing.png',                   # You can use an emoji or path to an image file
    layout='centered',                    # Use 'wide' or 'centered' to set the layout
    initial_sidebar_state='expanded', # Use 'expanded' or 'collapsed' to set the sidebar state
    menu_items={                      # Additional menu items in the hamburger menu
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Text 2 Speech Converter using *ElevenLabs API*. \n\n This app is created by [Tomique34](https://www.linkedin.com/in/tomasvince/)."
    }
)

# Load environment variables from .env file
load_dotenv()

# Get the current date and time for filename uniqueness
now = datetime.now()
date_string = now.strftime("%Y-%m-%d_%H-%M")

# Create an instance of the ElevenLabs client with the API key
elevenlabs_api_key = os.getenv('ELEVEN_API_KEY')
client = ElevenLabs(api_key=elevenlabs_api_key)



# Initialize an empty list to hold the voice names for Streamlit dropdown menu options
voice_names = []

# List all available Elevenlabs voices and print their details.
#supported_voices = client.voices.get_all()

try:
    supported_voices = client.voices.get_all()
except pydantic.ValidationError as e:
    st.error("Failed to fetch voices. Please check the API key and try again.")
    supported_voices = None

if supported_voices is not None:
    for voice in supported_voices.voices:  # Accessing the voices attribute directly
        gender = voice.labels.get('gender', 'Unknown')
        voice_names.append(voice.name)
else:
    st.error("No voices available. Please check your API response.")

# print("\n")
# print("***************************************************")
# print("Available Elevenlabs voices:")
# print("***************************************************")
print("\n")
#print(supported_voices) # Print the entire raw response

# Iterate over each voice in the response and print the required details.
for voice in supported_voices.voices:
    gender = voice.labels.get('gender', 'Unknown')
    voice_names.append(voice.name)
    #print(f"Voice ID: {voice.voice_id}, Name: {voice.name}, Category: {voice.category},Gender: {gender}")
print("\n")

# End of the script which list all available Elevenlabs voices

# Streamlit app interface
st.title('Text to Speech Generator using ElevenLabs API')

# Dropdown menu for voice selection
selected_voice = st.selectbox("Choose a voice for speech generation:", voice_names)

# Text area for user input
user_input_text = st.text_area("Enter the text you want to convert to speech:", height=150)

##########################################
# *** Beginning of Audio synthesis script 
##########################################

# Submit button to convert the text to speech
submit = st.button('Convert to Speech')

if submit:
    if user_input_text:
        # Process the conversion
        try:
            # Get the current date and time
            now = datetime.now()

            # Format the date and time as a string
            date_string = now.strftime("%Y-%m-%d_%H-%M")
            speech_file_path = Path("audio-outputs") / f"speech-{date_string}.mp3"

            # Create directory if it doesn't exist
            speech_file_directory = Path(__file__).parent / "audio-outputs"
            speech_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Define the path to the audio file, parameters for the speech model, and the manually typed input text for conversion to audio file
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

            # Display a message to inform the user that the file was created
            st.success("The audio file has been created successfully.")

            # Read the saved audio file in binary mode
            with open(speech_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Provide a link for the user to download the MP3 file
            st.download_button(label="Download Speech File",
                               data=audio_data,
                               file_name=speech_file_path.name,
                               mime="audio/mp3")
            
            # Display an audio player option to listen to the generated speech (Chrome browser supported)
            st.write("Listen to the generated speech using below built-in audio player:")
            st.audio(audio_data, format='audio/mp3', start_time=0)


        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please enter some text to convert to speech.")
else:
    st.info("INSTRUCTIONS: Select from supported voice, Enter text, and click the Convert button to create an audio file.")


##########################################
# *** End of Audio synthesis script 
##########################################

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
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # Check if the file is an actual file
        if os.path.isfile(file_path):
            # Check the file's modification time
            if os.stat(file_path).st_mtime < time.time() - max_age:
                try:
                    os.remove(file_path)
                    print("***************************************************")
                    print(f"*** Deleted following old generated speech files --> {file_path}")
                except Exception as e:
                    print(f"Error while deleting file {file_path}: {e}")

# You can call this function at the end of your Streamlit script
# to clean up the audio files periodically (e.g., files older than 10 minutes)
cleanup_files('./audio-outputs/', max_age=600)


