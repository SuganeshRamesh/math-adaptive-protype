"""
ML Model Training and Management
Handles training, evaluation, and persistence of the logistic regression model
"""

import json
import os
import pickle
import argparse
from typing import List, Dict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class MLModelManager:
    """
    Manages ML model lifecycle:
    - Training from performance data
    - Evaluation
    - Persistence
    - Inference
    """
    
    def __init__(self, model_path: str = 'models/difficulty_predictor.pkl'):
        """Initialize model manager."""
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        self.metrics = {}
    
    def load_performance_data(self, data_path: str = 'data/performance_logs.json') -> List[Dict]:
        """
        Load performance data from JSON logs.
        
        Args:
            data_path: Path to performance logs
            
        Returns:
            List of performance records
        """
        if not os.path.exists(data_path):
            print(f"❌ Data file not found: {data_path}")
            return []
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} session records")
        return data
    
    def extract_features(self, data: List[Dict]) -> tuple:
        """
        Extract features and targets from performance logs.
        
        Args:
            data: Performance logs
            
        Returns:
            (X, y) - Feature matrix and target vector
        """
        X = []
        y = []
        
        for session in data:
            responses = session.get('responses', [])
            
            if len(responses) < 3:
                continue
            
            for i in range(2, len(responses)):
                # Get metrics from previous responses
                prior_responses = responses[:i]
                prior_correct = sum(1 for r in prior_responses if r['is_correct'])
                prior_total = len(prior_responses)
                
                # Recent performance (last 3)
                recent_responses = prior_responses[-3:]
                recent_correct = sum(1 for r in recent_responses if r['is_correct'])
                recent_total = len(recent_responses)
                
                # Response times
                response_times = [r['response_time'] for r in recent_responses]
                avg_recent_time = sum(response_times) / len(response_times) if response_times else 0
                
                # Calculate consecutive correct (streak)
                consecutive = 0
                for r in reversed(prior_responses):
                    if r['is_correct']:
                        consecutive += 1
                    else:
                        break
                
                # Features
                accuracy = (prior_correct / prior_total * 100) if prior_total > 0 else 0
                recent_accuracy = (recent_correct / recent_total * 100) if recent_total > 0 else 0
                
                features = [
                    accuracy,
                    avg_recent_time,
                    consecutive,
                    recent_accuracy
                ]
                
                # Target: Is current response correct?
                target = 1 if responses[i]['is_correct'] else 0
                
                X.append(features)
                y.append(target)
        
        return np.array(X), np.array(y)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> bool:
        """
        Train logistic regression model.
        
        Args:
            X: Feature matrix
            y: Target vector
            
        Returns:
            True if training successful
        """
        if len(X) == 0:
            print("❌ No training data available")
            return False
        
        print(f"Training on {len(X)} samples...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_train = self.model.predict(X_train)
        
        self.metrics = {
            'train_accuracy': accuracy_score(y_train, y_pred_train),
            'test_accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0)
        }
        
        self.is_trained = True
        return True
    
    def evaluate(self) -> Dict[str, float]:
        """Get model evaluation metrics."""
        return self.metrics
    
    def save(self) -> bool:
        """Save trained model to disk."""
        if not self.is_trained:
            print("❌ Model not trained yet")
            return False
        
        os.makedirs(os.path.dirname(self.model_path) or '.', exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"✅ Model saved to {self.model_path}")
        return True
    
    def load(self) -> bool:
        """Load model from disk."""
        if not os.path.exists(self.model_path):
            print(f"⚠️ Model file not found: {self.model_path}")
            return False
        
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        self.is_trained = True
        print(f"✅ Model loaded from {self.model_path}")
        return True
    
    def full_pipeline(self, data_path: str = 'data/performance_logs.json') -> bool:
        """
        Complete training pipeline:
        1. Load data
        2. Extract features
        3. Train model
        4. Evaluate
        5. Save
        
        Args:
            data_path: Path to performance logs
            
        Returns:
            True if successful
        """
        print("🚀 Starting model training pipeline...")
        print()
        
        # Load data
        print("Step 1: Loading performance data...")
        data = self.load_performance_data(data_path)
        if not data:
            return False
        print()
        
        # Extract features
        print("Step 2: Extracting features...")
        X, y = self.extract_features(data)
        print(f"✅ Extracted {len(X)} training examples")
        print(f"   Classes: {np.unique(y, return_counts=True)[1]}")
        print()
        
        if len(X) < 10:
            print("❌ Insufficient training data (minimum 10 samples required)")
            return False
        
        # Train model
        print("Step 3: Training model...")
        if not self.train(X, y):
            return False
        print()
        
        # Evaluate
        print("Step 4: Evaluating model...")
        metrics = self.evaluate()
        print(f"✅ Training Accuracy: {metrics['train_accuracy']:.2%}")
        print(f"✅ Test Accuracy: {metrics['test_accuracy']:.2%}")
        print(f"✅ Precision: {metrics['precision']:.2%}")
        print(f"✅ Recall: {metrics['recall']:.2%}")
        print(f"✅ F1-Score: {metrics['f1']:.2%}")
        print()
        
        # Save model
        print("Step 5: Saving model...")
        if not self.save():
            return False
        
        print()
        print("✅ Pipeline complete!")
        return True


def main():
    """CLI for model training."""
    parser = argparse.ArgumentParser(description="Train ML difficulty predictor")
    parser.add_argument('--train', action='store_true', help='Train model')
    parser.add_argument('--data', default='data/performance_logs.json', help='Data path')
    parser.add_argument('--output', default='models/difficulty_predictor.pkl', help='Model output path')
    
    args = parser.parse_args()
    
    manager = MLModelManager(model_path=args.output)
    
    if args.train:
        success = manager.full_pipeline(data_path=args.data)
        exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
