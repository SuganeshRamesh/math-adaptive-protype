"""
Performance Tracker - Logs and analyzes user performance metrics
Tracks accuracy, response time, and learning patterns
"""

import json
from typing import Dict, List, Any
from collections import defaultdict


class PerformanceTracker:
    """
    Tracks detailed performance metrics for each question.
    
    Metrics tracked:
    - Correctness (correct/incorrect)
    - Response time
    - Difficulty level
    - Consecutive correct answers (streak)
    - Overall accuracy
    - Average response time
    """
    
    def __init__(self, user_name: str, session_mode: str = "rule_based"):
        """
        Initialize performance tracker.
        
        Args:
            user_name: Name of the user for logging
            session_mode: Adaptation mode being used
        """
        self.user_name = user_name
        self.session_mode = session_mode
        
        # Response history
        self.responses: List[Dict[str, Any]] = []
        
        # Running metrics
        self.correct_count = 0
        self.incorrect_count = 0
        self.consecutive_correct = 0
        self.max_consecutive_correct = 0
        self.total_response_time = 0.0
    
    def record_response(self, puzzle: Dict, user_answer: float, 
                       is_correct: bool, response_time: float, 
                       difficulty: str) -> None:
        """
        Record a user's response to a puzzle.
        
        Args:
            puzzle: The puzzle that was presented
            user_answer: The user's answer
            is_correct: Whether the answer was correct
            response_time: Time taken to respond (seconds)
            difficulty: Difficulty level of the puzzle
        """
        # Update counts
        if is_correct:
            self.correct_count += 1
            self.consecutive_correct += 1
            self.max_consecutive_correct = max(self.max_consecutive_correct, 
                                              self.consecutive_correct)
        else:
            self.incorrect_count += 1
            self.consecutive_correct = 0
        
        # Update timing
        self.total_response_time += response_time
        
        # Store full response record
        response_record = {
            'puzzle': puzzle,
            'user_answer': user_answer,
            'correct_answer': puzzle['answer'],
            'is_correct': is_correct,
            'response_time': response_time,
            'difficulty': difficulty,
            'question_number': len(self.responses) + 1
        }
        
        self.responses.append(response_record)
    
    def get_current_metrics(self) -> Dict[str, float]:
        """
        Get current session metrics.
        
        Returns:
            Dictionary with:
            - 'total_questions': Total questions answered
            - 'correct_count': Correct answers
            - 'incorrect_count': Incorrect answers
            - 'accuracy': Accuracy percentage (0-100)
            - 'avg_response_time': Average response time
            - 'consecutive_correct': Current streak
            - 'max_streak': Longest streak
            - 'recent_accuracy': Accuracy in last 3 questions
        """
        total = len(self.responses)
        
        if total == 0:
            return {
                'total_questions': 0,
                'correct_count': 0,
                'incorrect_count': 0,
                'accuracy': 0.0,
                'avg_response_time': 0.0,
                'consecutive_correct': 0,
                'max_streak': 0,
                'recent_accuracy': 0.0,
                'response_time_trend': 'stable'
            }
        
        accuracy = (self.correct_count / total) * 100
        avg_response_time = self.total_response_time / total
        
        # Calculate recent accuracy (last 3 questions)
        recent_responses = self.responses[-3:] if len(self.responses) >= 3 else self.responses
        recent_correct = sum(1 for r in recent_responses if r['is_correct'])
        recent_accuracy = (recent_correct / len(recent_responses)) * 100 if recent_responses else 0
        
        # Detect response time trend
        if len(self.responses) >= 3:
            recent_times = [r['response_time'] for r in self.responses[-3:]]
            older_times = [r['response_time'] for r in self.responses[:-3]]
            
            if older_times:
                recent_avg = sum(recent_times) / len(recent_times)
                older_avg = sum(older_times) / len(older_times)
                
                if recent_avg > older_avg * 1.2:
                    trend = 'slowing'
                elif recent_avg < older_avg * 0.8:
                    trend = 'improving'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'total_questions': total,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'accuracy': accuracy,
            'avg_response_time': avg_response_time,
            'consecutive_correct': self.consecutive_correct,
            'max_streak': self.max_consecutive_correct,
            'recent_accuracy': recent_accuracy,
            'response_time_trend': trend
        }
    
    def get_difficulty_breakdown(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance breakdown by difficulty level.
        
        Returns:
            Dictionary mapping difficulty level to metrics:
            {
                'Easy': {'accuracy': 80.0, 'count': 5, 'avg_time': 2.3},
                'Medium': {...},
                'Hard': {...}
            }
        """
        breakdown = defaultdict(lambda: {'correct': 0, 'total': 0, 'total_time': 0})
        
        for response in self.responses:
            difficulty = response['difficulty']
            breakdown[difficulty]['total'] += 1
            if response['is_correct']:
                breakdown[difficulty]['correct'] += 1
            breakdown[difficulty]['total_time'] += response['response_time']
        
        # Convert to percentages and averages
        result = {}
        for difficulty, stats in breakdown.items():
            total = stats['total']
            accuracy = (stats['correct'] / total) * 100 if total > 0 else 0
            avg_time = stats['total_time'] / total if total > 0 else 0
            
            result[difficulty] = {
                'accuracy': accuracy,
                'count': total,
                'avg_time': avg_time
            }
        
        return result
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive session summary.
        
        Returns:
            Dictionary with all key metrics for end-of-session display
        """
        metrics = self.get_current_metrics()
        difficulty_breakdown = self.get_difficulty_breakdown()
        
        return {
            **metrics,
            'difficulty_breakdown': difficulty_breakdown,
            'response_history_length': len(self.responses)
        }
    
    def export_for_ml_training(self) -> List[Dict[str, Any]]:
        """
        Export response data in format suitable for ML model training.
        
        Returns:
            List of feature dictionaries for model training
        """
        training_data = []
        
        for i, response in enumerate(self.responses):
            if i < 2:  # Need at least 2 prior responses for features
                continue
            
            # Get metrics up to this point (excluding current response)
            prior_responses = self.responses[:i]
            prior_correct = sum(1 for r in prior_responses if r['is_correct'])
            prior_total = len(prior_responses)
            
            # Recent performance
            recent_correct = sum(1 for r in prior_responses[-3:] if r['is_correct'])
            recent_total = min(3, len(prior_responses))
            
            # Features
            features = {
                'accuracy': (prior_correct / prior_total * 100) if prior_total > 0 else 0,
                'response_time': sum(r['response_time'] for r in prior_responses[-3:]) / min(3, len(prior_responses)) if prior_responses else 0,
                'consecutive_correct': sum(1 for r in prior_responses if r['is_correct']) - sum(1 for r in prior_responses if not r['is_correct']),
                'recent_accuracy': (recent_correct / recent_total * 100) if recent_total > 0 else 0,
            }
            
            # Target: Did difficulty increase in next step?
            # This would be determined by session logic, defaulting to None
            target = 1 if response['is_correct'] and prior_correct / prior_total > 0.8 else 0
            
            training_data.append({
                'features': features,
                'target': target,
                'current_difficulty': response['difficulty']
            })
        
        return training_data
