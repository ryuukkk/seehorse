import base64
import numpy as np
import cv2
import openai
import requests
import matplotlib.pyplot as plt
import os

print(os.chdir('../..'))
# print(os.getcwd())
with open('/home/crow/Iota/seehorse/src/predict/openai_key.txt', 'r') as f:
    API_KEY = f.read()


def encode_image(image_path):
    """
    Encodes an image file to a base64 string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def describe_image(image_path=None) -> str:
    """
    Reads an image from a file, encodes it, and uses OpenAI's API to describe it.

    Parameters:
    - image_path: str - The file path of the image to describe.

    Returns:
    - str - A description of the image or an error message.
    """
    if not image_path:
        return 'No image'

    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What’s in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 80
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        description = response_data['choices'][0]['message']['content']
    except Exception as e:
        description = e

    return description


def generate_response(prompt: str, description=None) -> str:
    """
    Generates a response based on the user's prompt and an image description using the Chat Completions API.

    Parameters:
    - prompt: str - The user's question or prompt.
    - description: str - The description of the image obtained from describe_image().

    Returns:
    - str - A generated response based on the prompt and description.
    """
    if not description:
        description = 'No image given'
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": "Act like a real human guiding the blind user. Given a description sorroundings and a user's prompt, determine if the prompt asks for a scene description. If so, respond based on the image description in very short. Include safety advice if any danger is detected. If the prompt does not seek a scene description, respond appropriately without referring to the image."},
        {"role": "user", "content": description},
        {"role": "user", "content": prompt}
    ]

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 50
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            return f"API error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Failed to generate response: {str(e)}"

response = generate_response('describe the scene', describe_image('/home/crow/Iota/seehorse/src/predict/pit.jpg'))
print(response)
