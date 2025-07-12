# app.py
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uuid
from chat_db import init_db, save_chat, get_all_sessions_latest_chats, clear_all_chats, delete_chat_by_id, get_session_chats
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'a_super_secret_key_that_should_be_changed_in_production')
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    current_session_id = request.json.get('session_id')

    if not current_session_id:
        return jsonify({'reply': "Error: Session ID not found in request. Please refresh the page or start a new chat."}), 400

    try:
        model = genai.GenerativeModel('models/gemma-3-4b-it')

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        session_history = get_session_chats(current_session_id)
        
        prompt_parts = [
            "You are a helpful and respectful general-purpose AI assistant. "
            "Your goal is to provide accurate and relevant information on a wide range of topics. "
            "Please be friendly and conversational in your responses. "
            "When appropriate, use Markdown for clear formatting, such as bolding for headings and bullet points or numbered lists for key information."
            "\n\n--- Conversation History ---\n"
        ]

        for turn in session_history:
            prompt_parts.append(f"User: {turn[0]}\nBot: {turn[1]}\n")
        
        prompt_parts.append(f"--- New User Query ---\nUser: {user_message}\nBot:")

        full_prompt = "".join(prompt_parts)

        response = model.generate_content(
            full_prompt,
            safety_settings=safety_settings,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=700
            )
        )

        if response.candidates and response.candidates[0].content.parts:
            bot_reply = response.candidates[0].content.parts[0].text.strip()
        else:
            bot_reply = "Sorry, I couldn't generate a response for that. Your query might have triggered safety filters, or it's outside my current capabilities. Please try rephrasing your question."
            if response.prompt_feedback and response.prompt_feedback.safety_ratings:
                print("Gemini Safety Block (Prompt Feedback):", response.prompt_feedback.safety_ratings)
            if response.candidates and response.candidates[0].finish_reason == 'SAFETY':
                print("Gemini Safety Block (Candidate Finish Reason):", response.candidates[0].safety_ratings)
            elif response.candidates and response.candidates[0].finish_reason:
                 print("Gemini Finish Reason (other):", response.candidates[0].finish_reason)

        save_chat(current_session_id, user_message, bot_reply)
        return jsonify({'reply': bot_reply})

    except Exception as e:
        print("Gemini API Error:", e)
        return jsonify({'reply': f"Sorry, I'm currently unable to process that request due to an internal error. Please try again later. (Error: {str(e)[:50]}...)"})

@app.route('/history', methods=['GET'])
def history():
    try:
        chats = get_all_sessions_latest_chats()
        formatted_chats = [{"id": chat[0], "session_id": chat[1], "user": chat[2], "bot": chat[3], "timestamp": chat[4]} for chat in chats]
        return jsonify({'history': formatted_chats})
    except Exception as e:
        print("Database Error (history):", e)
        return jsonify({'history': [], 'error': "Could not retrieve chat history."}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        clear_all_chats()
        session.pop('session_id', None)
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Database Error (clear_history):", e)
        return jsonify({'status': 'error', 'message': 'Failed to clear history.'}), 500

@app.route('/delete_chat/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    try:
        delete_chat_by_id(chat_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Database Error (delete_chat/{chat_id}):", e)
        return jsonify({'status': 'error', 'message': 'Failed to delete chat.'}), 500

@app.route('/get_session_conversation/<string:session_id>', methods=['GET'])
def get_session_conversation(session_id):
    try:
        conversation_data = get_session_chats(session_id)
        if conversation_data:
            formatted_conversation = [
                {"user": row[0], "bot": row[1], "timestamp": row[2]} for row in conversation_data
            ]
            return jsonify({'conversation': formatted_conversation})
        else:
            return jsonify({'error': 'Conversation not found for this session'}), 404
    except Exception as e:
        print(f"Database Error (get_session_conversation/{session_id}):", e)
        return jsonify({'error': 'Failed to retrieve conversation.'}), 500

if __name__ == '__main__':
    app.run(debug=True)