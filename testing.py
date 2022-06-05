from utils.FifteenApi import FifteenAPI


def main():
	print("Getting text")
	string = "What is the creepiest/most bizarre unsolved mystery in the world?"
	FifteenAPI().split_up_and_save("Twilight Sparkle", string, "example.wav")
	
main()