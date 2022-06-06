from utils.GoogleCloudSpeech import google_text_to_speech, list_voices
def main():
	print("Getting text")
	string = "What is the creepiest/most bizarre unsolved mystery in the world?"
	google_text_to_speech("Das ist ein Test", "example.mp3")
main()