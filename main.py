import speech_recognition as sr
import pyttsx3
import numpy as np
import os
import time
from datetime import datetime
# from dotenv import load_dotenv


CALLS = ["jarvis", "hey jarvis", "hello jarvis", "jarv", "jarvy", "what's up jarvis", "whats up jarvis", "hey jarv", "yo jarvis", "yo jarv"]
DISREGARD = ["disregard", "nothing", "forget it", "never mind", "bye", "stop", "ok bye", "bye jarvis", "all right by", "all right bye", "by", "no", "no by", "no bye", "buy", "buy jarvis", "all right buy"]

BASIC_REQUESTS = {

"time": ["what time is it", "time", "what's the time", "what is the time", "the time"],
"change voice": ["change your voice", "change voice", "different voice", "change voices", "use a different voice"],
"decrease volume": ["decrease volume", "lower volume", "turn it down", "too loud", "you're too loud"],
"increase volume": ["increase volume", "higher volume", "i can't hear you", "turn it up"],
"increase rate": ["increase speaking rate", "speak faster", "you talk too slow"],
"decrease rate": ["decrease speaking rate", "speak slower", "you talk too fast"]


}

ADVANCED_REQUESTS = ["set a timer", "shutdown"]


INVALID_THRESHOLD = 3 # Number of times you can 


CLAP_THRESHOLD = 125 # Amplitude needed to be considered a clap
DOUBLE_CLAP_THRESHOLD = 0.3 * 1000 # If user claps twice within 0.6 seconds, it's counted as a double clap

# load_dotenv("key.env")
# API_KEY = os.getenv("API_KEY")


def get_mic_input(mic: sr.Microphone, rec: sr.Recognizer) -> tuple[str, bool]:
	"""
	Using mic input, returns any words said, returns the string speech, and a boolean, True if the
	mic input was legible, otherwise False
	:rtype: tuple[str, bool]

	"""
	output = ""

	with mic as source:
		rec.adjust_for_ambient_noise(source, 0.5)
		try:
			audio = rec.listen(source, 10) # Wait up to 10 seconds for input

		except sr.exceptions.WaitTimeoutError:
			return output, False


		try:
			output = rec.recognize_google(audio).lower().strip()

		except sr.exceptions.UnknownValueError:

			if is_clap(audio):
				return "CLAP", True

			return output, False

	return output, True



def listen_for_jarvis(mic: sr.Microphone, rec: sr.Recognizer, engine: pyttsx3.Engine, name:str = None, recursive:bool = False) -> None:
	"""
	Listens if Jarvis has been called for, if a name is given then the introduction will include the name
	:rtype: None
	"""
	
	output = ""


	with mic as source:
		while output not in CALLS and "jarvis" not in output:
			rec.adjust_for_ambient_noise(source, 0.5)

			try:
				audio = rec.listen(source, 20)
				output = rec.recognize_google(audio).lower().strip()
				print(output)

			except (sr.exceptions.UnknownValueError, sr.exceptions.WaitTimeoutError) as e:
				continue

			except sr.exceptions.RequestError:
				engine.say("Internet connections issue, or API key is not valid, Jarvis is now unavailable.")
				engine.runAndWait()
				engine.stop()

				quit()

			time.sleep(0.5)


	if name is not None:
		engine.say(f"What can I do for you {name}.")

	else:
		engine.say("What can I do for you.")


	engine.runAndWait()

	request = ""
	valid = True

	while valid:
		req, valid = process_request(mic, rec, engine, name=name)

		if req in CALLS:
			if name is None:
				engine.say(f"Yes ?")

			else:
				engine.say(f"Yes {name} ?")


		if valid and req:
			print (req)
			engine.say("Anything else ?")
			engine.runAndWait()

		time.sleep(0.01)

	if name is not None:
		engine.say(f"Bye {name}.")

	else:
		engine.say(f"Bye.")

	engine.runAndWait()
	engine.stop()

	if recursive:
		listen_for_jarvis(mic, rec, engine, name=name, recursive=recursive)


def process_request(mic: sr.Microphone, rec: sr.Recognizer, engine: pyttsx3.Engine, name:str = None) -> tuple[str, bool]:
	"""
	Processes a request said in to the mic, and handles any action needed to be done afterwards,
	returns the request as a string and a boolean indicating whether the request was able to be fufilled.

	:rtype: tuple[str, bool]
	"""
	invalid_count = 0
	time_since_last_clap = DOUBLE_CLAP_THRESHOLD

	request = ""
	volume = engine.getProperty("volume") # Scale from 0.0 to 1.0
	rate = engine.getProperty("rate") # Rate in words per minute (wpm)


	while invalid_count < INVALID_THRESHOLD:
		request, valid = get_mic_input(mic, rec)

		if not valid:
			invalid_count += 1

			if invalid_count < INVALID_THRESHOLD:
				engine.say("I didn't get that, could you say that again ?")
				engine.runAndWait()
				engine.stop()

		elif request in DISREGARD or "bye" in request or "no" in request:
			return request, False


		else:
			break



	if invalid_count >= INVALID_THRESHOLD:
		return request, False



	# Handle basic requests

	if request in BASIC_REQUESTS["time"] or "time" in request:
		now = datetime.now()
		current_time = now.strftime("%I:%M %p")

		engine.say(f"It is currently {current_time}")

	elif request in BASIC_REQUESTS["change voice"]:
		engine = change_voice(mic, rec, engine)


	# Handle changes to the voice engine

	elif request in BASIC_REQUESTS["increase volume"]:
		if volume >= 1.0:
			engine.say("Max volume")

		else:
			volume += 0.05
			engine.setProperty("volume", volume)

			engine.say("Volume increased")

	elif request in BASIC_REQUESTS["decrease volume"]:
		if volume <= 0.05:
			engine.say("Minimum volume")

		else:
			volume -= 0.05
			engine.setProperty("volume", volume)

			engine.say("Volume decreased")

	elif request in BASIC_REQUESTS["increase rate"]:
		rate += 25
		engine.setProperty("rate", rate)
		engine.say("Rate of speech increased")


	elif request in BASIC_REQUESTS["decrease rate"]:
		if rate <= 25:
			engine.say("Minimum rate of speech")

		else:
			rate -= 25
			engine.setProperty("rate", rate)
			engine.say("Rate of speech decreased")


	# Handle remote shutdown / restart


	elif request == "shut down" or "shut down" in request:
		engine.say("Are you sure you want to shutdown ?")
		engine.runAndWait()
		engine.stop()

		answer, valid = get_mic_input(mic, rec)

		if valid and answer == "yes":
			engine.say("Shutting down.")
			engine.runAndWait()
			engine.stop()

			os.system("shutdown /s /t 0") # Shutdown after 0 seconds
			time.sleep(5) # Wait for system to shutdown

			return request, False

	elif request == "restart" or "restart" in request:
		engine.say("Are you sure you want to restart ?")
		engine.runAndWait()
		engine.stop()

		answer, valid = get_mic_input(mic, rec)

		if valid and answer == "yes":
			engine.say("Restarting")
			engine.runAndWait()
			engine.stop()

			os.system("shutdown /r /t 0") # Restart after 0 seconds
			return request, False


	elif request == "CLAP" and time.time() - time_since_last_clap >= DOUBLE_CLAP_THRESHOLD:
		# engine.say("User has clapped")
		print ("user has clapped")
		time_since_last_clap = time.time()

	elif request == "CLAP" and time.time() - time_since_last_clap < DOUBLE_CLAP_THRESHOLD:
		engine.say("User has double clapped")

		time_since_last_clap = DOUBLE_CLAP_THRESHOLD



	else:
		print(request)
		engine.say("Irrelevant request, ask again")
		request = ""



	engine.runAndWait()
	engine.stop()

	return request, True


def change_voice(mic: sr.Microphone, rec: sr.Recognizer, engine: pyttsx3.Engine) -> pyttsx3.Engine:
	"""
	Changes the voice of the engine as per the user's request, and returns the engine with the new voice
	:rtype: pyttsx3.Engine
	"""

	voices = engine.getProperty("voices")

	engine.say("I will cycle through voices, when i'm done talking, say skip to move to the next one, or stop to choose a voice.")
	engine.runAndWait()
	engine.stop()

	default_voice = engine.getProperty("voice")


	for voice in voices:
		engine.setProperty("voice", voice.id)
		engine.say("Hello I'm Jarvis your personal desktop assistant.")
		engine.runAndWait()
		engine.stop()

		output, valid = get_mic_input(mic, rec)


		if not valid:
			continue


		elif "stop" in output:
			engine.say("Voice changed successfully.")
			engine.runAndWait()
			engine.stop()
			
			break


	# If all voices are cycled through and one isn't chosen, set voice back to the one used before asking to change
	else:
		engine.setProperty("voice", default_voice)


	return engine



def is_clap(audio: sr.AudioData, clap_threshold:int = CLAP_THRESHOLD) -> bool:
	"""
	Given an sr.AudioData object, will return True if the max amplitude of the audio is greater
	than clap_threshold.
	:rtype: bool
	"""


	audio_bytes = audio.get_raw_data()

	byte_arr = np.frombuffer(audio_bytes, dtype=np.int16)

	print (f"Clap amplitude: {str(np.max(np.abs(byte_arr)))}")

	if np.max(np.abs(byte_arr)) >= clap_threshold: # See if the audio amplitude spikes above the clap threshold
		return True

	return False







if __name__ == "__main__":
	print("Call for Jarvis")

	engine = pyttsx3.init()
	mic = sr.Microphone(device_index=2)
	rec = sr.Recognizer()



	engine.setProperty("rate", 180)
	engine.setProperty("volume", 1.0)

	engine.say("Hello I'm Jarvis your personal desktop assistant, say my name then state your request.")
	engine.runAndWait()
	engine.stop()




	listen_for_jarvis(mic, rec, engine, "Aashir", recursive=True)


