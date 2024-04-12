import os

os.chdir('..')

from django.shortcuts import render
from django.http import JsonResponse
from src.predict import predict


# Create your views here.

def home(request):
    return render(request, 'index.html')


def process_data(request):
    if request.method == 'POST':
        # Get the data from the POST request
        data = request.POST.get('data')

        print(data)
        # Process the data (example: convert it to uppercase)
        processed_data = predict.generate_response(data)

        # Return a JsonResponse with the processed data
        return JsonResponse({'processed_data': processed_data})
    else:
        # Return an error response if the request method is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=405)
