"""
Adaptive Engine - Core adaptation logic (Rule-Based and ML-Based)
Decides when and how to adjust puzzle difficulty based on performance
"""

import os
import pickle
from typing import Dict, Literal
from sklearn.linear_model import LogisticRegression
import numpy as np


class AdaptiveEngine:
    """
    Determines next difficulty level based on performance metrics.
    
    Supports two modes:
    1. Rule-Based: Threshold-driven logic (fast, transparent)
    2. ML-Based: Logistic regression model (learns from data)
    """
    
    # Rule-based thresholds
    RULE_BASED_THRESHOLDS = {
        'increase': {
            'min_accuracy': 80,  # >= 80% accuracy
            'max_avg_time': 5,   # <= 5 seconds average
            'min_consecutive': 2  # At least 2 correct in a row
        },
        'decrease': {
            'max_accuracy': 60,  # < 60% accuracy
            'min_avg_time': 8    # >= 8 seconds average
        }
    }
    
    def __init__(self, mode: str = "rule_based"):
        """
        Initialize adaptation engine.
        
        Args:
            mode: "rule_based" or "ml_based"
        """
        self.mode = mode
        self.model = None
        self.is_trained = False
        
        if mode == "ml_based":
            self._load_or_initialize_model()
    
    def _load_or_initialize_model(self):
        """Load trained ML model or initialize new one."""
        model_path = 'models/difficulty_predictor.pkl'
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                print("✅ Loaded trained ML model")
            except Exception as e:
                print(f"⚠️ Could not load model: {e}. Using rule-based fallback.")
                self.model = None
                self.is_trained = False
        else:
            # Initialize untrained model
            self.model = LogisticRegression(random_state=42, max_iter=1000)
            self.is_trained = False
    
    def get_next_action(self, performance_metrics: Dict, 
                       current_difficulty: str) -> Literal["increase", "maintain", "decrease"]:
        """
        Determine whether to increase, maintain, or decrease difficulty.
        
        Args:
            performance_metrics: Current performance metrics from tracker
            current_difficulty: Current difficulty level
            
        Returns:
            Action: "increase", "maintain", or "decrease"
        """
        if self.mode == "rule_based":
            return self._get_action_rule_based(performance_metrics, current_difficulty)
        elif self.mode == "ml_based" and self.is_trained:
            return self._get_action_ml_based(performance_metrics, current_difficulty)
        else:
            # Fallback to rule-based if ML model not trained
            return self._get_action_rule_based(performance_metrics, current_difficulty)
    
    def _get_action_rule_based(self, performance_metrics: Dict, 
                              current_difficulty: str) -> Literal["increase", "maintain", "decrease"]:
        """
        Rule-based adaptation logic using thresholds.
        
        Rules:
        - INCREASE: Accuracy >= 80% AND Avg Time <= 5s AND Consecutive Correct >= 2
        - DECREASE: Accuracy < 60% OR Avg Time >= 8s
        - MAINTAIN: Otherwise
        """
        accuracy = performance_metrics['accuracy']
        avg_time = performance_metrics['avg_response_time']
        consecutive = performance_metrics['consecutive_correct']
        
        increase_thresholds = self.RULE_BASED_THRESHOLDS['increase']
        decrease_thresholds = self.RULE_BASED_THRESHOLDS['decrease']
        
        # Check increase conditions
        if (accuracy >= increase_thresholds['min_accuracy'] and
            avg_time <= increase_thresholds['max_avg_time'] and
            consecutive >= increase_thresholds['min_consecutive']):
            
            if current_difficulty != "Hard":
                return "increase"
        
        # Check decrease conditions
        if (accuracy < decrease_thresholds['max_accuracy'] or
            avg_time >= decrease_thresholds['min_avg_time']):
            
            if current_difficulty != "Easy":
                return "decrease"
        
        # Default: maintain
        return "maintain"
    
    def _get_action_ml_based(self, performance_metrics: Dict, 
                            current_difficulty: str) -> Literal["increase", "maintain", "decrease"]:
        """
        ML-based adaptation using logistic regression.
        
        Features used:
        - Accuracy
        - Response time
        - Consecutive correct answers
        - Recent accuracy trend
        
        Returns:
        - "increase" if probability > 0.6
        - "decrease" if accuracy < 50% (safety threshold)
        - "maintain" otherwise
        """
        # Extract features
        features = np.array([[
            performance_metrics['accuracy'],
            performance_metrics['avg_response_time'],
            performance_metrics['consecutive_correct'],
            performance_metrics['recent_accuracy']
        ]])
        
        # Predict probability of success at next difficulty
        try:
            probability = self.model.predict_proba(features)[0][1]
        except Exception as e:
            print(f"ML prediction error: {e}. Using rule-based.")
            return self._get_action_rule_based(performance_metrics, current_difficulty)
        
        # Safety check: if accuracy very low, decrease
        if performance_metrics['accuracy'] < 50 and current_difficulty != "Easy":
            return "decrease"
        
        # Decision based on predicted probability
        if probability > 0.6 and current_difficulty != "Hard":
            return "increase"
        elif probability < 0.4 and current_difficulty != "Easy":
            return "decrease"
        else:
            return "maintain"
    
    @staticmethod
    def train_model(training_data: list, save_path: str = 'models/difficulty_predictor.pkl'):
        """
        Train logistic regression model on historical data.
        
        Args:
            training_data: List of training examples from PerformanceTracker.export_for_ml_training()
            save_path: Path to save trained model
        """
        if not training_data:
            print("❌ No training data available")
            return False
        
        # Extract features and targets
        X = np.array([d['features'].values() for d in training_data])
        y = np.array([d['target'] for d in training_data])
        
        # Train model
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X, y)
        
        # Save model
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        with open(save_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"✅ Model trained and saved to {save_path}")
        print(f"   Training accuracy: {model.score(X, y):.2%}")
        
        return True


class HybridAdaptiveEngine(AdaptiveEngine):
    """
    Hybrid approach combining rule-based and ML-based logic.
    
    Uses confidence scores from both approaches:
    - Rule-based: Binary (confident decision or not)
    - ML-based: Probability scores
    
    When both agree: Follow immediately
    When they disagree: Use ML confidence as tiebreaker
    """
    
    def get_next_action(self, performance_metrics: Dict,
                       current_difficulty: str) -> Literal["increase", "maintain", "decrease"]:
        """
        Get adaptation action using hybrid logic.
        
        Combines rule-based transparency with ML flexibility.
        """
        # Get both predictions
        rule_action = self._get_action_rule_based(performance_metrics, current_difficulty)
        ml_action = self._get_action_ml_based(performance_metrics, current_difficulty) if self.is_trained else rule_action
        
        # If both agree, use that action
        if rule_action == ml_action:
            return rule_action
        
        # If they disagree, use rule-based as primary (safer)
        # and only use ML if very confident
        if self.is_trained:
            accuracy = performance_metrics['accuracy']
            # Only trust ML for edge cases
            if rule_action == "maintain" and 70 <= accuracy <= 85:
                return ml_action
        
        return rule_action
