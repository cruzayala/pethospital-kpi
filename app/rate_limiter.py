"""
Shared rate limiter instance for the application
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Single Limiter instance used across the app
limiter = Limiter(key_func=get_remote_address)

