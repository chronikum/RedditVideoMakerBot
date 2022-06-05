import enum
import os
import re
import time
import json
import logging
from moviepy.editor import concatenate_audioclips, AudioFileClip

import requests
from requests.exceptions import ConnectionError

# taken from https://github.com/wafflecomposite/15.ai-Python-API.
# We are using the 15.ai API, which is just fucking great.

class FifteenAPI:

	logger = logging.getLogger('15API')
	logger.addHandler(logging.StreamHandler())

	max_text_len = 200

	tts_headers = {
		"accept": "application/json, text/plain, */*",
		"accept-encoding": "gzip, deflate, br",
		"accept-language": "en-US,en;q=0.9",
		"access-control-allow-origin": "*",
		"content-type": "application/json;charset=UTF-8",
		"origin": "https://fifteen.ai",
		"referer": "https://fifteen.ai/app",
		"sec-fetch-dest": "empty",
		"sec-fetch-mode": "cors",
		"sec-fetch-site": "same-site",
		"user-agent": "python-requests 15.ai-Python-API(https://github.com/wafflecomposite/15.ai-Python-API)"
	}

	tts_url = "https://api.15.ai/app/getAudioFile5"
	audio_url = "https://cdn.15.ai/audio/"


	def __init__(self, show_debug = False):
		if show_debug:
			self.logger.setLevel(logging.DEBUG)
		else:
			self.logger.setLevel(logging.WARNING)
		self.logger.info("FifteenAPI initialization")


	def get_tts_raw(self, character, text):

		resp = {"status": "NOT SET", "data": None}


		text_len = len(text)
		if text_len > self.max_text_len:
			self.logger.warning(f'Text too long ({text_len} > {self.max_text_len}), trimming to {self.max_text_len} symbols')
			text = text[:self.max_text_len - 1]

		if not text.endswith(".") and not text.endswith("!") and not text.endswith("?"):
			if len(text) < 140:
				text += '.'
			else:
				text = text[:-1] + '.'

		self.logger.info(f'Target text: [{text}]')
		self.logger.info(f'Character: [{character}]')

		data = json.dumps({"text": text, "character": character, "emotion": "Contextual"})

		self.logger.info('Waiting for 15.ai response...')

		try:
			response = requests.post(self.tts_url, data=data, headers=self.tts_headers)
		except requests.exceptions.ConnectionError as e:
			resp["status"] = f"ConnectionError ({e})"
			self.logger.error(f"ConnectionError ({e})")
			return resp

		if response.status_code == 200:

			resp["response"] = response.json()
			resp["audio_uri"] = resp["response"]["wavNames"][0]

			try:
				responseAudio = requests.get(self.audio_url+resp["audio_uri"], headers=self.tts_headers)
				resp["status"] = "OK"
				resp["data"] = responseAudio.content
				self.logger.info(f"15.ai API response success")
				return resp
			except requests.exceptions.ConnectionError as e:
				resp["status"] = f"ConnectionError ({e})"
				self.logger.error(f"ConnectionError ({e})")
				return resp
 
		else:
			self.logger.error(f'15.ai API request error, Status code: {response.status_code}')
			resp["status"] = f'15.ai API request error, Status code: {response.status_code}'
		return resp
		
	def save_to_file(self, character, text, filename=None):
		tts = self.get_tts_raw(character, text)
		if tts["status"] == "OK" and tts["data"] is not None:
			if filename is None:
				char_filename_part = "".join(x for x in character[:10] if x.isalnum())
				text_filename_part = "".join(x for x in text[:16] if x.isalnum())
				filename = f"15ai-{char_filename_part}-{text_filename_part}-{round(time.time())}.wav"
			if not filename.endswith(".wav"):
				filename += ".wav"
			f = open(filename, 'wb')
			f.write(tts["data"])
			f.close()
			self.logger.info(f"File saved: {filename}")
			return {"status": tts["status"], "filename": filename}
		else:
			return {"status": tts["status"], "filename": None}
		
	# splits string up in portions of s symbols and returns a list
	def chunker(self, s, w):
		return [s[i:i + w] for i in range(0, len(s), w)]
		
	# replaces all non-alpha characters with their counterpart
	def replace_number_with_spoken_word(self, text):
		for number in text.split():
			if number.isdigit():
				text = text.replace(number, num2words(int(number), lang="en_US"))
		text = text.replace("%", "Percent")
		return text
	
	# splits up the text into chunks of 200 symbols and then
	# calls get_tts_raw for each chunk.
	# After that it combines all the chunks into one file.
	def split_up_and_save(self, character, text, filename=None):
		
		text = self.replace_number_with_spoken_word(text)
		chunks = self.chunker(text, 200)
		infiles = []
		print(f"Splitting up text into {len(chunks)} chunks")
		for idx, chunk in enumerate(chunks):
			tts = self.get_tts_raw(character, chunk)
			if tts["status"] == "OK" and tts["data"] is not None:
				tts_data = tts["data"]
			f = open(f"temp/{idx}_temp_file_.wav", 'ab')
			f.write(tts_data)
			f.close()
			os.system(f"ffmpeg -y -i temp/{idx}_temp_file_.wav temp/{idx}_temp_file_.mp3")
			infiles.append(f"temp/{idx}_temp_file_.mp3")
		data = []
		clips = [AudioFileClip(c) for c in infiles]
		final_clip = concatenate_audioclips(clips)
		final_clip.write_audiofile(filename)