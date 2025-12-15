"""
Math Adventures - Adaptive Learning System
Main entry point for the adaptive learning session
"""

import json
import os
from datetime import datetime
from typing import Optional
from src.puzzle_generator import PuzzleGenerator
from src.tracker import PerformanceTracker
from src.adaptive_engine import AdaptiveEngine
from src.utils import format_time, clear_screen, print_header


class AdaptiveLearningSession:
    """
    Orchestrates an adaptive learning session.
    
    Manages:
    - User interactions
    - Puzzle presentation
    - Performance tracking
    - Real-time difficulty adaptation
    - Session summary
    """
    
    DIFFICULTY_LEVELS = {1: "Easy", 2: "Medium", 3: "Hard"}
    ADAPTATION_MODES = {1: "rule_based", 2: "ml_based"}
    
    def __init__(self, user_name: str, initial_difficulty: str, adaptation_mode: str = "rule_based"):
        """
        Initialize a learning session.
        
        Args:
            user_name: Name of the learner
            initial_difficulty: Starting difficulty level ("Easy", "Medium", "Hard")
            adaptation_mode: "rule_based" or "ml_based"
        """
        self.user_name = user_name
        self.current_difficulty = initial_difficulty
        self.adaptation_mode = adaptation_mode
        self.session_start_time = datetime.now()
        
        # Initialize components
        self.puzzle_gen = PuzzleGenerator()
        self.tracker = PerformanceTracker(user_name=user_name, session_mode=adaptation_mode)
        self.adaptive_engine = AdaptiveEngine(mode=adaptation_mode)
        
        # Session state
        self.question_count = 0
        self.responses = []  # List of (puzzle, answer, is_correct, response_time)
        self.difficulty_history = [initial_difficulty]
        self.running = True
        
    def run(self, max_questions: int = 10):
        """
        Run an adaptive learning session.
        
        Args:
            max_questions: Maximum number of puzzles in this session (default: 10)
        """
        clear_screen()
        print_header("Welcome to Math Adventures!")
        print(f"📚 Hello, {self.user_name}!")
        print(f"📊 Adaptation Mode: {self.adaptation_mode.replace('_', ' ').title()}")
        print(f"🎯 Starting Difficulty: {self.current_difficulty}")
        print("-" * 60)
        print()
        
        while self.running and self.question_count < max_questions:
            self._present_puzzle()
            
            # Check if we should continue
            if self.question_count < max_questions:
                continue_prompt = input("\nContinue? (y/n): ").strip().lower()
                if continue_prompt != 'y':
                    self.running = False
            else:
                self.running = False
        
        # Display session summary
        self._display_summary()
        
        # Save session data
        self._save_session()
    
    def _present_puzzle(self):
        """Present a single puzzle and get user response."""
        # Generate puzzle at current difficulty
        puzzle = self.puzzle_gen.generate_puzzle(self.current_difficulty)
        self.question_count += 1
        
        # Display puzzle
        clear_screen()
        print_header(f"Math Adventures - Question {self.question_count}")
        print(f"User: {self.user_name}")
        print(f"Difficulty: {self.current_difficulty} {self._difficulty_indicator()}")
        print("-" * 60)
        print(f"\n{puzzle['question']}")
        print()
        
        # Get user response with timing
        import time
        response_start = time.time()
        
        try:
            user_answer = float(input("Your answer: "))
            response_time = time.time() - response_start
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            return
        
        # Check correctness
        is_correct = abs(user_answer - puzzle['answer']) < 0.01  # Allow small floating-point error
        
        # Provide immediate feedback
        if is_correct:
            print(f"✅ Correct! (Response time: {format_time(response_time)})")
        else:
            print(f"❌ Incorrect. The correct answer is {puzzle['answer']}")
            print(f"   (Response time: {format_time(response_time)})")
        
        # Track performance
        self.tracker.record_response(
            puzzle=puzzle,
            user_answer=user_answer,
            is_correct=is_correct,
            response_time=response_time,
            difficulty=self.current_difficulty
        )
        
        self.responses.append({
            'puzzle': puzzle,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'response_time': response_time
        })
        
        # Adapt difficulty (every 2+ questions or on specific triggers)
        if self.question_count >= 2:
            old_difficulty = self.current_difficulty
            performance_metrics = self.tracker.get_current_metrics()
            
            # Get adaptation recommendation
            action = self.adaptive_engine.get_next_action(
                performance_metrics=performance_metrics,
                current_difficulty=old_difficulty
            )
            
            if action == "increase" and old_difficulty != "Hard":
                self.current_difficulty = self._increase_difficulty()
                print(f"\n📈 Performing well! Difficulty increased to {self.current_difficulty}.")
                self.difficulty_history.append(self.current_difficulty)
            elif action == "decrease" and old_difficulty != "Easy":
                self.current_difficulty = self._decrease_difficulty()
                print(f"\n📉 Let's try an easier level to build confidence. Difficulty decreased to {self.current_difficulty}.")
                self.difficulty_history.append(self.current_difficulty)
            else:
                print(f"\n➡️ Maintaining difficulty level.")
    
    def _difficulty_indicator(self) -> str:
        """Return a visual indicator for difficulty level."""
        indicators = {
            "Easy": "⭐",
            "Medium": "⭐⭐",
            "Hard": "⭐⭐⭐"
        }
        return indicators.get(self.current_difficulty, "")
    
    def _increase_difficulty(self) -> str:
        """Move to next difficulty level."""
        difficulty_order = ["Easy", "Medium", "Hard"]
        current_index = difficulty_order.index(self.current_difficulty)
        return difficulty_order[min(current_index + 1, len(difficulty_order) - 1)]
    
    def _decrease_difficulty(self) -> str:
        """Move to previous difficulty level."""
        difficulty_order = ["Easy", "Medium", "Hard"]
        current_index = difficulty_order.index(self.current_difficulty)
        return difficulty_order[max(current_index - 1, 0)]
    
    def _display_summary(self):
        """Display comprehensive session summary."""
        clear_screen()
        print_header("📊 Session Summary")
        print()
        
        # Basic stats
        metrics = self.tracker.get_session_summary()
        
        print(f"User: {self.user_name}")
        print(f"Duration: {self._session_duration()}")
        print()
        
        print("─" * 60)
        print("PERFORMANCE METRICS")
        print("─" * 60)
        print(f"Questions Answered: {metrics['total_questions']}")
        print(f"Correct Answers: {metrics['correct_count']} ({metrics['accuracy']:.1f}%)")
        print(f"Incorrect Answers: {metrics['incorrect_count']}")
        print(f"Average Response Time: {format_time(metrics['avg_response_time'])}")
        print()
        
        print("─" * 60)
        print("DIFFICULTY PROGRESSION")
        print("─" * 60)
        print(f"Started: {self.difficulty_history[0]}")
        print(f"Final: {self.difficulty_history[-1]}")
        print(f"Changes: {len(self.difficulty_history) - 1}")
        print(f"Progression Path: {' → '.join(self.difficulty_history)}")
        print()
        
        print("─" * 60)
        print("RECOMMENDATIONS")
        print("─" * 60)
        
        if metrics['accuracy'] >= 80:
            print("✨ Excellent! You're mastering this level.")
            print("💡 Next time, try starting at a higher difficulty.")
        elif metrics['accuracy'] >= 60:
            print("👍 Good job! You're making progress.")
            print("💡 Practice will help you get faster and more accurate.")
        else:
            print("💪 Keep practicing! You'll improve with time.")
            print("💡 Don't worry about speed—focus on accuracy first.")
        
        print()
        print("─" * 60)
        print("🎉 Great job, {}! Keep practicing!".format(self.user_name))
        print("─" * 60)
    
    def _session_duration(self) -> str:
        """Calculate and format session duration."""
        duration = datetime.now() - self.session_start_time
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    
    def _save_session(self):
        """Save session data to JSON for analysis and model training."""
        os.makedirs('data', exist_ok=True)
        
        session_record = {
            'timestamp': self.session_start_time.isoformat(),
            'user_name': self.user_name,
            'adaptation_mode': self.adaptation_mode,
            'initial_difficulty': self.difficulty_history[0],
            'final_difficulty': self.difficulty_history[-1],
            'total_questions': self.question_count,
            'responses': [
                {
                    'puzzle': r['puzzle'],
                    'user_answer': r['user_answer'],
                    'is_correct': r['is_correct'],
                    'response_time': r['response_time'],
                    'difficulty': self.difficulty_history[
                        min(len(self.difficulty_history) - 1,
                            self.responses.index(r) if r in self.responses else 0)
                    ]
                }
                for r in self.responses
            ]
        }
        
        # Append to performance logs
        log_file = 'data/performance_logs.json'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(session_record)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"\n✅ Session saved to {log_file}")


def main():
    """Main entry point for interactive session."""
    # Clear screen and show welcome
    clear_screen()
    print_header("🎮 Math Adventures - Adaptive Learning System")
    print()
    
    # Get user information
    user_name = input("Enter your name: ").strip()
    if not user_name:
        user_name = "Learner"
    
    # Select initial difficulty
    print("\nSelect initial difficulty:")
    print("1 = Easy (single digits)")
    print("2 = Medium (double digits)")
    print("3 = Hard (larger numbers)")
    
    while True:
        try:
            difficulty_choice = int(input("Your choice (1-3): "))
            initial_difficulty = AdaptiveLearningSession.DIFFICULTY_LEVELS.get(difficulty_choice)
            if initial_difficulty:
                break
            print("❌ Please enter 1, 2, or 3.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    # Select adaptation mode
    print("\nSelect adaptation mode:")
    print("1 = Rule-Based (threshold-driven, fast)")
    print("2 = ML-Based (learns from data, requires history)")
    
    while True:
        try:
            mode_choice = int(input("Your choice (1-2): "))
            adaptation_mode = AdaptiveLearningSession.ADAPTATION_MODES.get(mode_choice)
            if adaptation_mode:
                break
            print("❌ Please enter 1 or 2.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    # Create and run session
    session = AdaptiveLearningSession(
        user_name=user_name,
        initial_difficulty=initial_difficulty,
        adaptation_mode=adaptation_mode
    )
    
    session.run(max_questions=10)


if __name__ == "__main__":
    main()
