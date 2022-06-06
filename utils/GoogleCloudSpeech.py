from google.cloud import texttospeech

def google_text_to_speech(text, filename):
	# Instantiates a client
	client = texttospeech.TextToSpeechClient()

	# Set the text input to be synthesized
	synthesis_input = texttospeech.SynthesisInput(text=text)

	# Build the voice request, select the language code ("en-US") and the ssml
	# voice gender ("neutral")
	voice = texttospeech.VoiceSelectionParams(
		language_code="en-GB", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
	)

	# Select the type of audio file you want returned
	audio_config = texttospeech.AudioConfig(
		audio_encoding=texttospeech.AudioEncoding.MP3
	)

	# Perform the text-to-speech request on the text input with the selected
	# voice parameters and audio file type
	response = client.synthesize_speech(
		input=synthesis_input, voice=voice, audio_config=audio_config
	)

	# The response's audio_content is binary.
	with open(filename, "wb") as out:
		out.write(response.audio_content)
		print('Audio content written to file "output.mp3"')
		
def list_voices():
    """Lists the available voices."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    for voice in voices.voices:
        # Display the voice's name. Example: tpc-vocoded
        print(f"Name: {voice.name}")

        # Display the supported language codes for this voice. Example: "en-US"
        for language_code in voice.language_codes:
            print(f"Supported language: {language_code}")

        ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

        # Display the SSML Voice Gender
        print(f"SSML Voice Gender: {ssml_gender.name}")

        # Display the natural sample rate hertz for this voice. Example: 24000
        print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")
