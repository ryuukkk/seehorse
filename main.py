import pygame
import cv2
import speech_recognition as sr
import threading
from src import predict
from pygame import mixer
import os

# Initialize Pygame and Mixer for audio
pygame.init()
mixer.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Seehorse Assistance")

# Webcam setup
cap = cv2.VideoCapture(0)


def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = 'temp_audio.mp3'
    tts.save(filename)
    mixer.music.load(filename)
    mixer.music.play()
    while mixer.music.get_busy():  # wait for audio to finish playing
        pygame.time.Clock().tick(10)
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

    listening_thread = threading.Thread(target=continuous_listen)
    listening_thread.start()


def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # Clear screen with white
        pygame.display.flip()  # Update the full display

    pygame.quit()
    cap.release()


if __name__ == "__main__":
    main()
