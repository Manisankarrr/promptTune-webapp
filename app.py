from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS # <-- REMOVED
from gradio_client import Client
import logging
import os
import requests

# --- Configuration ---
app = Flask(__name__, template_folder='templates')

# --- REMOVE CORS INITIALIZATION ---
# CORS(app) # <-- REMOVED
# ----------------------------------

logging.basicConfig(level=logging.INFO)

# Your deployed Hugging Face Space ID
SPACE_ID = "Manisankarrr/PromptTune" 

try:
    gradio_client = Client(SPACE_ID)
    logging.info(f"Gradio Client initialized for Space: {SPACE_ID}")
except Exception as e:
    logging.error(f"Failed to initialize Gradio Client for {SPACE_ID}: {e}")
    gradio_client = None


# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main HTML page (index.html) from the templates folder."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_prompt():
    """Proxies the prompt generation request to the deployed Gradio API."""
    if gradio_client is None:
        return jsonify({"error": "Service unavailable: Gradio Client failed to initialize."}), 503
        
    try:
        data = request.get_json()
        user_input = data.get('prompt')
        
        if not user_input:
            return jsonify({"error": "Missing 'prompt' input."}), 400

        optimized_prompt, final_response = gradio_client.predict(
            user_input=user_input,
            api_name="/process_submission"
        )

        return jsonify({
            "optimized_prompt": optimized_prompt,
            "final_response": final_response
        })
        
    except Exception as e:
        app.logger.error(f"Gradio /generate API call failed: {e}")
        return jsonify({"error": f"Internal API error during prompt generation: {e}"}), 500

@app.route('/feedback', methods=['POST'])
def handle_feedback_proxy():
    """Proxies the user feedback data (rating) to the deployed Gradio API."""
    if gradio_client is None:
        return jsonify({"error": "Service unavailable: Gradio Client failed to initialize."}), 503

    try:
        data = request.get_json()
        rating = data.get('rating') # Expects: "👍 Excellent" or "👎 Needs Work"

        if not rating:
            return jsonify({"error": "Missing 'rating' value."}), 400

        feedback_status = gradio_client.predict(
            rating_value=rating,
            api_name="/handle_feedback"
        )
        
        return jsonify({"status": feedback_status})

    except Exception as e:
        app.logger.error(f"Gradio /feedback API call failed: {e}")
        return jsonify({"error": f"Internal API error. Feedback not logged: {e}"}), 500

# --- REMOVED THE app.run() BLOCK ---
# Vercel handles the server startup, so this block is not needed.