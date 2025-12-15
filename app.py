"""
Streamlit GUI for Math Adventures - Kid-Friendly Interface
Creates a colorful, engaging web interface for the adaptive learning system
"""

import streamlit as st
import time
from datetime import datetime
from src.puzzle_generator import PuzzleGenerator
from src.tracker import PerformanceTracker
from src.adaptive_engine import AdaptiveEngine
import json
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="🎮 Math Adventures",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for kid-friendly design
st.markdown("""
<style>
    /* Main background - bright and friendly */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 800px;
    }
    
    /* Title styling */
    .title-main {
        text-align: center;
        color: #fff;
        font-size: 3.5em;
        font-weight: bold;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
        animation: bounce 1s;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #fff;
        font-size: 1.5em;
        margin-bottom: 1.5rem;
    }
    
    /* Card styling */
    .card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2em;
        font-weight: bold;
        padding: 15px 40px;
        border-radius: 50px;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 15px;
        border: 2px solid #667eea;
        padding: 12px;
        font-size: 1.1em;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #155724;
        padding: 1.5rem;
        border-radius: 15px;
        font-size: 1.3em;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(132, 250, 176, 0.4);
    }
    
    /* Error message */
    .error-message {
        background: linear-gradient(135deg, #fa8072 0%, #ff6b6b 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        font-size: 1.3em;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    /* Info message */
    .info-message {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 216, 155, 0.4);
    }
    
    /* Question display */
    .question-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px 0 rgba(245, 87, 108, 0.37);
    }
    
    /* Difficulty badge */
    .difficulty-easy {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #155724;
    }
    
    .difficulty-medium {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #856404;
    }
    
    .difficulty-hard {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
        color: #721c24;
    }
    
    /* Stats display */
    .stats-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stat-label {
        font-size: 0.9em;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 2em;
        font-weight: bold;
        color: #667eea;
    }
    
    /* Emoji animations */
    .emoji-bounce {
        display: inline-block;
        animation: bounce 0.6s;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    /* Progress bar */
    .progress-bar {
        background: #ddd;
        border-radius: 20px;
        height: 30px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "session" not in st.session_state:
    st.session_state.session = None
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Helper functions
def get_difficulty_color(difficulty):
    """Return color for difficulty level"""
    colors = {
        "Easy": "🟢",
        "Medium": "🟡",
        "Hard": "🔴"
    }
    return colors.get(difficulty, "⚪")

def get_difficulty_gradient(difficulty):
    """Return gradient class for difficulty"""
    classes = {
        "Easy": "difficulty-easy",
        "Medium": "difficulty-medium",
        "Hard": "difficulty-hard"
    }
    return classes.get(difficulty, "")

def show_welcome():
    """Welcome page"""
    st.markdown("""
    <div style='text-align: center; color: white; padding: 2rem;'>
        <div style='font-size: 4em; margin: 1rem 0;'>🎮 Math Adventures 🎲</div>
        <div style='font-size: 1.8em; margin: 1rem 0;'>🧮 Learn Math the Fun Way! ✨</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='card'>
            <h2 style='text-align: center; color: #667eea;'>Welcome! 👋</h2>
            <p style='font-size: 1.1em; text-align: center; color: #333;'>
                Get ready for an exciting math adventure! 
                Solve puzzles, unlock achievements, and level up your math skills! 🌟
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # User name input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_name = st.text_input(
            "What's your name?",
            placeholder="Enter your name",
            label_visibility="collapsed",
            key="user_name_input"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Difficulty selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='color: white; font-size: 1.2em; font-weight: bold; margin-bottom: 1rem;'>Choose your starting difficulty:</div>", unsafe_allow_html=True)
        
        difficulty = st.radio(
            "Difficulty",
            ["🟢 Easy (1-9)", "🟡 Medium (10-50)", "🔴 Hard (50-100)"],
            label_visibility="collapsed"
        )
        
        difficulty_map = {
            "🟢 Easy (1-9)": "Easy",
            "🟡 Medium (10-50)": "Medium",
            "🔴 Hard (50-100)": "Hard"
        }
        selected_difficulty = difficulty_map[difficulty]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Adaptation mode selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='color: white; font-size: 1.2em; font-weight: bold; margin-bottom: 1rem;'>Choose adaptation style:</div>", unsafe_allow_html=True)
        
        adaptation = st.radio(
            "Adaptation",
            ["⚙️ Rule-Based (Fast & Smart)", "🤖 ML-Based (Learning)"],
            label_visibility="collapsed"
        )
        
        adaptation_map = {
            "⚙️ Rule-Based (Fast & Smart)": "rule_based",
            "🤖 ML-Based (Learning)": "ml_based"
        }
        selected_adaptation = adaptation_map[adaptation]
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Adventure!", use_container_width=True, key="start_btn"):
            if user_name.strip():
                st.session_state.session = {
                    'user_name': user_name,
                    'initial_difficulty': selected_difficulty,
                    'adaptation_mode': selected_adaptation,
                    'current_difficulty': selected_difficulty,
                    'puzzle_gen': PuzzleGenerator(),
                    'tracker': PerformanceTracker(user_name=user_name, session_mode=selected_adaptation),
                    'adaptive_engine': AdaptiveEngine(mode=selected_adaptation),
                    'question_count': 0,
                    'responses': [],
                    'difficulty_history': [selected_difficulty],
                    'start_time': datetime.now(),
                }
                st.session_state.page = "playing"
                st.rerun()
            else:
                st.error("Please enter your name to start! 😊")

def show_playing():
    """Main game page"""
    session = st.session_state.session

    # --- Keep / init current puzzle in session_state ---
    if "current_puzzle" not in st.session_state:
        st.session_state.current_puzzle = session["puzzle_gen"].generate_puzzle(
            session["current_difficulty"]
        )

    puzzle = st.session_state.current_puzzle

    # Header with user info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown(
            f"<div style='color: white; font-size: 1.3em; font-weight: bold;'>👤 {session['user_name']}</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div style='color: white; font-size: 1.3em; font-weight: bold; text-align: center;'>❓ {session['question_count'] + 1}</div>",
            unsafe_allow_html=True,
        )
    with col3:
        difficulty = session["current_difficulty"]
        emoji = get_difficulty_color(difficulty)
        st.markdown(
            f"<div style='color: white; font-size: 1.3em; font-weight: bold; text-align: right;'>{emoji} {difficulty}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<hr style='border-color: rgba(255,255,255,0.3); margin: 1rem 0;'>",
        unsafe_allow_html=True,
    )

    # Display question with large text
    st.markdown(
        f"""
        <div class='question-box'>
            {puzzle['operand1']} {puzzle['operation']} {puzzle['operand2']} = ?
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Input for answer
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_answer = st.number_input(
            "Your answer:",
            value=0.0,
            step=1.0,
            label_visibility="collapsed",
            key=f"answer_{session['question_count']}",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "✅ Check Answer",
            use_container_width=True,
            key=f"submit_{session['question_count']}",
        ):
            # Record response time
            response_time = 2.0  # TODO: measure actual time
            is_correct = abs(user_answer - puzzle["answer"]) < 0.01

            # Update tracker
            session["tracker"].record_response(
                puzzle=puzzle,
                user_answer=user_answer,
                is_correct=is_correct,
                response_time=response_time,
                difficulty=session["current_difficulty"],
            )

            session["responses"].append(
                {
                    "puzzle": puzzle,
                    "user_answer": user_answer,
                    "is_correct": is_correct,
                    "response_time": response_time,
                }
            )

            session["question_count"] += 1

            # Show result
            if is_correct:
                st.markdown(
                    """
                    <div class='success-message'>
                        ✅ CORRECT! Awesome job! 🎉
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class='error-message'>
                        ❌ Not quite! The answer is {puzzle['answer']} 💪
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            time.sleep(2)

            # Adapt difficulty if needed (after 2 questions)
            if session["question_count"] >= 2:
                metrics = session["tracker"].get_current_metrics()
                action = session["adaptive_engine"].get_next_action(
                    performance_metrics=metrics,
                    current_difficulty=session["current_difficulty"],
                )

                old_difficulty = session["current_difficulty"]

                if action == "increase" and old_difficulty != "Hard":
                    difficulty_order = ["Easy", "Medium", "Hard"]
                    current_idx = difficulty_order.index(old_difficulty)
                    session["current_difficulty"] = difficulty_order[current_idx + 1]
                    session["difficulty_history"].append(
                        session["current_difficulty"]
                    )
                    st.markdown(
                        """
                        <div class='info-message'>
                            📈 Difficulty increased! You're doing great!
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    time.sleep(1.5)
                elif action == "decrease" and old_difficulty != "Easy":
                    difficulty_order = ["Easy", "Medium", "Hard"]
                    current_idx = difficulty_order.index(old_difficulty)
                    session["current_difficulty"] = difficulty_order[current_idx - 1]
                    session["difficulty_history"].append(
                        session["current_difficulty"]
                    )
                    st.markdown(
                        """
                        <div class='info-message'>
                            📉 Let's try an easier level to build confidence!
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    time.sleep(1.5)

            # Decide next step
            if session["question_count"] < 10:
                # Generate NEXT puzzle and rerun
                st.session_state.current_puzzle = session[
                    "puzzle_gen"
                ].generate_puzzle(session["current_difficulty"])
                st.rerun()
            else:
                st.session_state.page = "summary"
                st.rerun()

def show_summary():
    """Summary page"""
    session = st.session_state.session
    metrics = session['tracker'].get_session_summary()
    
    st.markdown("""
    <div style='text-align: center; color: white; padding: 2rem;'>
        <div style='font-size: 4em; margin: 1rem 0;'>🎉 Session Complete! 🎉</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stats display
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>📊 Accuracy</div>
            <div class='stat-value'>{metrics['accuracy']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>⏱️ Avg Time</div>
            <div class='stat-value'>{metrics['avg_response_time']:.1f}s</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>✅ Correct</div>
            <div class='stat-value'>{metrics['correct_count']}/{metrics['total_questions']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>🔥 Max Streak</div>
            <div class='stat-value'>{metrics['max_streak']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Progression
    progression_text = " → ".join(session['difficulty_history'])
    st.markdown(f"""
    <div class='card'>
        <h3 style='color: #667eea; text-align: center;'>📈 Your Journey</h3>
        <p style='font-size: 1.2em; text-align: center; color: #333;'>{progression_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendations
    if metrics['accuracy'] >= 80:
        recommendation = "✨ Excellent! You're a math star! Try starting at a higher level next time!"
        color = "#84fab0"
    elif metrics['accuracy'] >= 60:
        recommendation = "👍 Good job! Keep practicing and you'll improve even more!"
        color = "#ffd89b"
    else:
        recommendation = "💪 Keep going! Math gets easier with practice!"
        color = "#fa8072"
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {color} 0%, rgba(255,255,255,0.1) 100%); 
                padding: 1.5rem; border-radius: 15px; text-align: center; 
                font-size: 1.2em; font-weight: bold; color: #333; margin: 1rem 0;'>
        {recommendation}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔄 Play Again", use_container_width=True):
                st.session_state.session = None
                st.session_state.page = "welcome"
                st.rerun()
        
        with col_b:
            if st.button("📊 View Stats", use_container_width=True):
                st.session_state.page = "stats"
                st.rerun()

def show_stats():
    """Detailed stats page"""
    session = st.session_state.session
    
    st.markdown("""
    <div style='color: white; font-size: 2.5em; font-weight: bold; text-align: center; margin: 1rem 0;'>
        📊 Detailed Statistics
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    metrics = session['tracker'].get_session_summary()
    difficulty_breakdown = metrics.get('difficulty_breakdown', {})
    
    # Overall stats
    st.markdown("""
    <div class='card'>
        <h3 style='color: #667eea;'>Overall Performance</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Questions", metrics['total_questions'])
        st.metric("Correct Answers", metrics['correct_count'])
    with col2:
        st.metric("Accuracy", f"{metrics['accuracy']:.1f}%")
        st.metric("Average Time", f"{metrics['avg_response_time']:.2f}s")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Difficulty breakdown
    st.markdown("""
    <div class='card'>
        <h3 style='color: #667eea;'>Performance by Difficulty</h3>
    </div>
    """, unsafe_allow_html=True)
    
    for difficulty, stats in difficulty_breakdown.items():
        emoji = get_difficulty_color(difficulty)
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;'>
            <strong>{emoji} {difficulty}</strong><br>
            Accuracy: {stats['accuracy']:.1f}% | Questions: {stats['count']} | Avg Time: {stats['avg_time']:.2f}s
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Back button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Summary", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()

# Main app routing
if st.session_state.page == "welcome":
    show_welcome()
elif st.session_state.page == "playing":
    show_playing()
elif st.session_state.page == "summary":
    show_summary()
elif st.session_state.page == "stats":
    show_stats()

# Footer
st.markdown("""
<hr style='border-color: rgba(255,255,255,0.2); margin: 2rem 0;'>
<div style='text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9em;'>
    suganesh r 
</div>
""", unsafe_allow_html=True)
