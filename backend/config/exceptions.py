# core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is None:
        # If the exception is not handled by DRF, return a custom JSON response
        response = Response(
            {'error': 'Database currently unavailable. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response