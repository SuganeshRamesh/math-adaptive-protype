"""
Math Adventures - Adaptive Learning System
Package initialization
"""

__version__ = "1.0.0"
__author__ = "Suganesh R"
__description__ = "AI-Powered Adaptive Learning Prototype for Math Education"

from src.main import AdaptiveLearningSession
from src.puzzle_generator import PuzzleGenerator
from src.tracker import PerformanceTracker
from src.adaptive_engine import AdaptiveEngine, HybridAdaptiveEngine
from src.ml_model import MLModelManager

__all__ = [
    'AdaptiveLearningSession',
    'PuzzleGenerator',
    'PerformanceTracker',
    'AdaptiveEngine',
    'HybridAdaptiveEngine',
    'MLModelManager'
]
