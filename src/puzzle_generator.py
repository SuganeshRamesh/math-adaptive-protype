"""
Puzzle Generator - Creates age-appropriate math problems
Generates puzzles at three difficulty levels: Easy, Medium, Hard
"""

import random
from typing import Dict, Any


class PuzzleGenerator:
    """
    Generates math puzzles dynamically based on difficulty level.
    
    Difficulty Levels:
    - Easy: Single-digit operations (1-9)
    - Medium: Double-digit operations (10-50)
    - Hard: Multi-digit operations (50-100)
    
    Operations: Addition, Subtraction, Multiplication, Division
    """
    
    OPERATIONS = ['+', '-', '×', '÷']
    
    DIFFICULTY_RANGES = {
        'Easy': {
            'min': 1,
            'max': 9,
            'operations': ['+', '-', '×'],  # No division for Easy
            'description': 'Single-digit operations'
        },
        'Medium': {
            'min': 10,
            'max': 50,
            'operations': ['+', '-', '×', '÷'],
            'description': 'Double-digit operations'
        },
        'Hard': {
            'min': 50,
            'max': 100,
            'operations': ['+', '-', '×', '÷'],
            'description': 'Multi-digit operations'
        }
    }
    
    def generate_puzzle(self, difficulty: str) -> Dict[str, Any]:
        """
        Generate a single math puzzle.
        
        Args:
            difficulty: "Easy", "Medium", or "Hard"
            
        Returns:
            Dictionary with:
            - 'question': Problem statement
            - 'operand1': First number
            - 'operand2': Second number
            - 'operation': The operation (+, -, ×, ÷)
            - 'answer': Correct answer
            - 'difficulty': Difficulty level
        """
        config = self.DIFFICULTY_RANGES[difficulty]
        
        # Randomly select operation
        operation = random.choice(config['operations'])
        
        # Generate operands based on difficulty
        operand1 = random.randint(config['min'], config['max'])
        operand2 = random.randint(config['min'], config['max'])
        
        # Calculate answer based on operation
        if operation == '+':
            answer = operand1 + operand2
        elif operation == '-':
            # Ensure positive result for subtraction
            operand1, operand2 = max(operand1, operand2), min(operand1, operand2)
            answer = operand1 - operand2
        elif operation == '×':
            answer = operand1 * operand2
        elif operation == '÷':
            # Ensure whole number division
            answer = random.randint(config['min'], config['max'])
            operand1 = answer * operand2
        
        # Format question
        question = f"{operand1} {operation} {operand2} = ?"
        
        return {
            'question': question,
            'operand1': operand1,
            'operand2': operand2,
            'operation': operation,
            'answer': answer,
            'difficulty': difficulty
        }
    
    def generate_multiple(self, difficulty: str, count: int = 5) -> list:
        """
        Generate multiple puzzles.
        
        Args:
            difficulty: "Easy", "Medium", or "Hard"
            count: Number of puzzles to generate
            
        Returns:
            List of puzzle dictionaries
        """
        return [self.generate_puzzle(difficulty) for _ in range(count)]
