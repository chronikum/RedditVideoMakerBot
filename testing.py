from utils.GoogleCloudSpeech import google_text_to_speech, list_voices
def main():
	print("Getting text")
	string = "What is the creepiest/most bizarre unsolved mystery in the world?"
	google_text_to_speech("not me, but my mom before i was born. she was riding in a convertible with a friend of hers. they came to an intersection and the  friend wasn't paying attention and lost control of the vehicle. there was a big rig going through the intersection and they went  right under the trailer. my mom ducked, the driver didn't not. driver was decapitated, my mom was lucky and only ended up with a  scalp full of glass and some serious psychological trauma. she had to get over two hundred stitches in her scalp but nothing else  significant.", "example.mp3")
main()