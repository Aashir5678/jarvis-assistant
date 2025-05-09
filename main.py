import speech_recognition as sr
import pyttsx3
from os import getenv
from datetime import datetime
from dotenv import load_dotenv


CALLS = ["jarvis", "hey jarvis", "hello jarvis", "jarv", "jarvy", "what's up jarvis", "whats up jarvis", "hey jarv", "yo jarvis", "yo jarv"]
DISREGARD = ["disregard", "nothing", "forget it", "never mind", "bye", "stop", "ok bye", "bye jarvis", "all right by", "all right bye", "by", "no", "no by", "no bye"]

BASIC_REQUESTS = {

"time": ["what time is it", "time", "what's the time", "what is the time", "the time"],
"change voice": ["change your voice", "change voice", "different voice", "change voices", "use a different voice"],
"decrease volume": ["decrease volume", "lower volume", "turn it down", "too loud", "you're too loud"],
"increase volume": ["increase volume", "higher volume", "i can't hear you", "turn it up"],
"increase rate": ["increase speaking rate", "speak faster", "you talk too slow"],
"decrease rate": ["decrease speaking rate", "speak slower", "you talk too fast"]


}

ADVANCED_REQUESTS = {}


INVALID_THRESHOLD = 3 # Number of times you can 

load_dotenv("key.env")
API_KEY = getenv("API_KEY")



def listen_for_jarvis(mic, rec, engine, name=None, recursive=False):
	output = ""

	with mic as source:
		while output not in CALLS or "jarvis" not in output:
			rec.adjust_for_ambient_noise(source)
			audio = rec.listen(source)


			try:
				output = rec.recognize_google(audio).lower().strip()

			except sr.exceptions.UnknownValueError:
				continue

			engine.runAndWait()
			engine.stop()



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


	if name is not None:
		engine.say(f"Bye {name}.")

	else:
		engine.say(f"Bye.")

	engine.runAndWait()
	engine.stop()

	if recursive:
		listen_for_jarvis(mic, rec, engine, name=name, recursive=recursive)


def process_request(mic, rec, engine, name=None):
	invalid_count = 0
	request = ""

	while invalid_count < INVALID_THRESHOLD:
		with mic as source:
			rec.adjust_for_ambient_noise(source)
			audio = rec.listen(source)

			try:
				request = rec.recognize_google(audio).lower().strip()

				if request in DISREGARD or "bye" in request or "no" in request:
					return request, False

				break


			except sr.exceptions.UnknownValueError:
				
				invalid_count += 1

				if invalid_count < INVALID_THRESHOLD:
					engine.say("I didn't get that, could you say that again ?")
					engine.runAndWait()
					engine.stop()




	if invalid_count >= INVALID_THRESHOLD:
		return request, False

	if request in BASIC_REQUESTS["time"]:
		now = datetime.now()
		current_time = now.strftime("%I:%M %p")

		engine.say(f"It is currently {current_time}")

	elif request in BASIC_REQUESTS["change voice"]:
		engine = change_voice(mic, rec, engine)



	else:
		print(request)
		engine.say("Irrelevant request, ask again")
		request = ""




	engine.runAndWait()
	engine.stop()

	return request, True


def change_voice(mic, rec, engine):
	voices = engine.getProperty("voices")

	engine.say("I will cycle through voices, when i'm done talking, say skip to move to the next one, or stop to choose a voice.")
	engine.runAndWait()
	engine.stop()

	default_voice = engine.getProperty("voice")


	for voice in voices:
		engine.setProperty("voice", voice.id)
		engine.say("Hello I'm Jarvis your personal desktop assistant, say my name then state your request.")
		engine.runAndWait()
		engine.stop()

		with mic as source:
			rec.adjust_for_ambient_noise(source)
			audio = rec.listen(source)

			try:
				output = rec.recognize_google(audio).lower().strip()


			except sr.exceptions.UnknownValueError:
				continue


		if "stop" in output:
			engine.say("Voice changed successfully.")
			engine.runAndWait()
			engine.stop()
			
			break

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


