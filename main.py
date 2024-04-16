import tkinter as tk
import cv2
import speech_recognition as sr
from threading import Thread
from src import predict
from gtts import gTTS
from playsound import playsound
import os

# Setup the webcam capture
cap = cv2.VideoCapture(0)

def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = 'temp_audio.mp3'
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

def listen_and_respond():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    listening = True

    def recognize_speech():
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Request failed"

    def continuous_listen():
        while listening:
            command = recognize_speech()
            if command:
                # Capture frame from webcam
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite('current_frame.jpg', frame)
                    response = predict.generate_response(command, predict.describe_image('current_frame.jpg'))
                    speak(response)
                else:
                    speak("Failed to capture the image.")

    listening_thread = Thread(target=continuous_listen)
    listening_thread.start()

    return listening_thread

# GUI setup
root = tk.Tk()
root.geometry("400x300")

start_btn = tk.Button(root, text="Start", command=listen_and_respond)
start_btn.pack(pady=20)

stop_btn = tk.Button(root, text="Stop", command=lambda: setattr(listen_and_respond(), 'listening', False))
stop_btn.pack(pady=20)

root.mainloop()
