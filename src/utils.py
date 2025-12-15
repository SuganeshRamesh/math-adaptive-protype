"""
Utility functions for the Math Adventures system
"""

import os
import sys


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text: str, width: int = 60):
    """
    Print formatted header.
    
    Args:
        text: Header text
        width: Width of header box
    """
    print("=" * width)
    print(text.center(width))
    print("=" * width)


def format_time(seconds: float) -> str:
    """
    Format seconds into readable time string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "2.3s")
    """
    return f"{seconds:.1f}s"


def get_user_input(prompt: str, input_type=str, valid_options=None):
    """
    Get validated user input.
    
    Args:
        prompt: Input prompt
        input_type: Expected data type (int, float, str)
        valid_options: List of valid options (if applicable)
        
    Returns:
        Validated user input
    """
    while True:
        try:
            user_input = input(prompt).strip()
            
            # Check if empty
            if not user_input:
                print("❌ Input cannot be empty. Please try again.")
                continue
            
            # Convert to type
            converted = input_type(user_input)
            
            # Check against valid options
            if valid_options and converted not in valid_options:
                print(f"❌ Please enter one of: {valid_options}")
                continue
            
            return converted
            
        except ValueError:
            print(f"❌ Invalid input. Please enter a {input_type.__name__}.")


def print_divider(char: str = "-", width: int = 60):
    """Print a dividing line."""
    print(char * width)


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ️ {message}")


def print_warning(message: str):
    """Print warning message."""
    print(f"⚠️ {message}")
