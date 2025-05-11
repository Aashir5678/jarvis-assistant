import speech_recognition as sr
import pyttsx3
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
		rec.adjust_for_ambient_noise(source)
		audio = rec.listen(source)


		try:
			output = rec.recognize_google(audio).lower().strip()

		except sr.exceptions.UnknownValueError:
			return output, False

	return output, True



def listen_for_jarvis(mic: sr.Microphone, rec: sr.Recognizer, engine: pyttsx3.Engine, name=None, recursive=False) -> None:
	"""
	Listens if Jarvis has been called for, if a name is given then the introduction will include the name
	:name: str
	:recursive: bool
	:rtype: None
	"""
	
	output = ""
	# while output not in CALLS or "jarvis" not in output:
	# 	output, valid = get_mic_input(mic, rec)

	# 	if not valid:
	# 		continue

	# 	elif 




	with mic as source:
		while output not in CALLS and "jarvis" not in output:
			rec.adjust_for_ambient_noise(source)
			audio = rec.listen(source)


			try:
				output = rec.recognize_google(audio).lower().strip()
				print(output)

			except sr.exceptions.UnknownValueError:
				continue

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

		print (req)
		if req in CALLS and name is not None:
			engine.say(f"Yes {name} ?")
			engine.runAndWait()

		elif req in CALLS:
			engine.say(f"Yes ?")
			engine.runAndWait()

		if valid and req:
			engine.say("Anything else ?")
			engine.runAndWait()

		time.sleep(0.1)

	if name is not None:
		engine.say(f"Bye {name}.")

	else:
		engine.say(f"Bye.")

	engine.runAndWait()
	engine.stop()

	if recursive:
		listen_for_jarvis(mic, rec, engine, name=name, recursive=recursive)


def process_request(mic: sr.Microphone, rec: sr.Recognizer, engine: pyttsx3.Engine, name=None) -> tuple[str, bool]:
	"""
	Processes a request said in to the mic, and handles any action needed to be done afterwards,
	returns the request as a string and a boolean indicating whether the request was able to be fufilled.

	:name: str
	:rtype: tuple[str, bool]
	"""
	invalid_count = 0
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

	if request in BASIC_REQUESTS["time"]:
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




if __name__ == "__main__":
	print("Call for Jarvis")

	engine = pyttsx3.init()
	mic = sr.Microphone()
	rec = sr.Recognizer()


	engine.setProperty("rate", 180)
	engine.setProperty("volume", 1.0)
	engine.setProperty("voice", 1.0)



	engine.say("Hello I'm Jarvis your personal desktop assistant, say my name then state your request.")
	engine.runAndWait()
	engine.stop()


	listen_for_jarvis(mic, rec, engine, "Aashir", recursive=True)


