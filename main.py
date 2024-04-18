import pygame
import cv2
import speech_recognition as sr
import threading
from src.predict import predict
from pygame import mixer
import numpy as np
from gtts import gTTS
import io

# Initialize Pygame and Mixer for audio
pygame.init()
mixer.init()
screen_width, screen_height = 1366, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Seehorse")
font = pygame.font.Font(None, 24)  # Smaller font for better fit

# Define layout regions
button_rect = pygame.Rect(10, 10, 100, 50)  # Start/Stop button at the top left
listening_indicator_rect = pygame.Rect(10, 70, 200, 20)  # "Listening..." indicator right below the button

# Before modifying these numbers, run once to check your screen's aspect ratio
camera_width, camera_height = 840, 472  # Adjusted size, maintaining 16:9 ratio
camera_rect = pygame.Rect(screen_width - camera_width - 10, 10, camera_width, camera_height)

text_recognized_rect = pygame.Rect(10, 520, 390, 290)  # Recognized text at the bottom left
text_spoken_rect = pygame.Rect(screen_width - camera_width - 10, 520, 390, 290)  # Spoken text at the bottom right

# Webcam setup
cap = cv2.VideoCapture(0)
listening = False  # Control variable for speech recognition
last_recognized_text = ""
last_spoken_text = ""
is_listening = False
is_speaking = False

def speak(text):
    global is_speaking, is_listening, last_spoken_text
    last_spoken_text = text  # Update the text that will be displayed
    is_speaking = True
    mixer.music.stop()  # Stop any ongoing audio
    tts = gTTS(text=text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    mixer.music.load(mp3_fp)
    mixer.music.play()
    while mixer.music.get_busy():  # Wait for audio to finish playing
        pygame.time.Clock().tick(10)
        pygame.display.flip()  # Make sure display updates during speaking
    is_speaking = False
    is_listening = True
    if listening:
        threading.Thread(target=listen_and_respond).start()


def wrap_text(text, rect, font):
    """ Wrap text to fit into rect. """
    word_list = text.split(' ')
    lines = []
    current_line = []
    for word in word_list:
        line_test = ' '.join(current_line + [word])
        if font.size(line_test)[0] > rect.width:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))
    return lines

# Do not modify this, or bad things will happen (also, remove this comment before final)
def listen_and_respond():
    global is_listening, last_recognized_text
    is_listening = True
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        is_listening = False
    try:
        command = recognizer.recognize_google(audio)
        last_recognized_text = command
        if command:
            ret, frame = cap.read()
            if ret:
                response = predict.generate_response(command, predict.describe_image(frame))
                speak(response)
    except sr.UnknownValueError:
        speak("Could not understand audio")
    except sr.RequestError:
        speak("Request failed")

def toggle_listen():
    global listening, is_listening
    listening = not listening
    if listening:
        is_listening = True
        threading.Thread(target=listen_and_respond).start()
    else:
        is_listening = False

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    toggle_listen()

        screen.fill((255, 255, 255))  # Clear screen with white

        # Draw button
        pygame.draw.rect(screen, (0, 128, 255), button_rect)
        text = font.render('Start' if not listening else 'Stop', True, (255, 255, 255))
        screen.blit(text, (button_rect.x + 5, button_rect.y + 10))

        # Update camera feed
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (camera_width, camera_height))
            camera_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(camera_surface, camera_rect.topleft)

        # Display recognized text
        lines = wrap_text(last_recognized_text, text_recognized_rect, font)
        base_y = text_recognized_rect.top
        for line in lines:
            text_surf = font.render(line, True, (0, 0, 0))
            screen.blit(text_surf, (text_recognized_rect.x + 5, base_y))
            base_y += text_surf.get_height()

        # Display spoken text
        lines = wrap_text(last_spoken_text, text_spoken_rect, font)
        base_y = text_spoken_rect.top
        for line in lines:
            text_surf = font.render(line, True, (0, 0, 0))
            screen.blit(text_surf, (text_spoken_rect.x + 5, base_y))
            base_y += text_surf.get_height()

        # Update listening indicator
        if is_listening:
            listening_text_surf = font.render("Listening...", True, (255, 0, 0))
            screen.blit(listening_text_surf, listening_indicator_rect.topleft)

        pygame.display.flip()  # Update the full display

    pygame.quit()
    cap.release()

if __name__ == "__main__":
    main()
