from utils.GoogleCloudSpeech import google_text_to_speech, list_voices
def main():
	print("Getting text")
	string = "What is the creepiest/most bizarre unsolved mystery in the world?"
	google_text_to_speech("This is a simple test to see if text to speech works.", "example.mp3")
main()