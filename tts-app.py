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

# Load environment variables from .env file
load_dotenv()

# Get the current date and time for filename uniqueness
now = datetime.now()
date_string = now.strftime("%Y-%m-%d_%H-%M")

# Suppress DeprecationWarning
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Create an instance of the ElevenLabs client with the API key
elevenlabs_api_key = os.getenv('ELEVEN_API_KEY')
client = ElevenLabs(api_key=elevenlabs_api_key)

# Define the path to the text file
text_file_path = Path(__file__).parent / "text-for-conversion.txt"




# List all available Elevenlabs voices and print their details.
#supported_voices = client.voices.get_all()

try:
    supported_voices = client.voices.get_all()
except pydantic.ValidationError as e:
    print("Failed to parse response: ", e)
    supported_voices = None

if supported_voices is not None:
    voice_names = []
    for voice in supported_voices.voices:  # Accessing the voices attribute directly
        gender = voice.labels.get('gender', 'Unknown')
        voice_names.append(voice.name)
        print(f"Voice ID: {voice.voice_id}, Name: {voice.name}, Category: {voice.category}, Gender: {gender}")
    
    if not voice_names:
        print("No voices found, please check the API response structure.")
else:
    print("No valid voices data retrieved.")

# print("\n")
# print("***************************************************")
# print("Available Elevenlabs voices:")
# print("***************************************************")
# print("\n")
#print(supported_voices) # Print the entire raw response

# Iterate over each voice in the response and print the required details.
for voice in supported_voices.voices:
    gender = voice.labels.get('gender', 'Unknown')
    voice_names.append(voice.name)
    #print(f"Voice ID: {voice.voice_id}, Name: {voice.name}, Category: {voice.category},Gender: {gender}")
print("\n")

# End of the script which list all available Elevenlabs voices

# Assuming voice_names is already populated with the names of available voices
for index, name in enumerate(voice_names, start=1):
    print(f"{index}: {name}")

# Ask the user to select a voice for generating the speech audio
user_choice = input("Please choose a voice by typing the number next to it: ")

# Validate the user's choice
try:
    choice_index = int(user_choice) - 1  # Convert to zero-based index
    if choice_index < 0 or choice_index >= len(voice_names):
        raise ValueError("Choice out of range")
except ValueError as e:
    print("Invalid choice, please run the script again and select a valid number.")
    exit()

# Retrieve the selected voice name
selected_voice_name = voice_names[choice_index]
print("\n")
print("*****************************************************")
print(f"You have selected the following voice: {selected_voice_name}")
print("*****************************************************")
print("\n")

##########################################
# *** Beginning of Audio synthesis script 
##########################################

# Open the text file and read its content
with open(text_file_path, 'r') as in_file:
    input_text = in_file.read()


# Generate the speech audio using Elevenlabs API from the provided text
try:
    response = client.generate(
      text=input_text,
      voice=selected_voice_name,
      model="eleven_multilingual_v2"
    )
except Exception as e:
    print(f"An error occurred: {e}")
    # Handle the error or exit

# Define the path to save the audio file, ensuring the directory exists
# 1. Check if the directory for the audio file exists, and create it if it doesn't
speech_file_directory = Path(__file__).parent / "audio-outputs"
speech_file_directory.parent.mkdir(parents=True, exist_ok=True)

# Define the path to the audio file, parameters for the speech model, and the manually typed input text for conversion to audio file
speech_file_path = speech_file_directory / f"speech-{date_string}.mp3"

# Save the response to a file
with open(speech_file_path, 'wb') as out_file:
    for chunk in response:
        out_file.write(chunk)
        
print("\n")
print("***************************************************")
print(f" Generated Audio file saved to --> {speech_file_path}")
print("***************************************************")
print("\n")

##########################################
# *** End of Audio synthesis script 
##########################################

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


