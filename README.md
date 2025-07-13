# 💬 AI Chatbot using Flask & GEMINI AI API

This is a general-purpose AI chatbot built using **Python**, **Flask**, and **GEMINI AI API**. The chatbot responds to user messages and generates intelligent replies using OpenAI's powerful language models.

## 🚀 Features

- Conversational AI using Gemini AI API  
- Flask-based Python backend  
- Simple and responsive frontend using HTML, CSS, JS  
- API key management with `.env` for security  
- Chat history stored using JSON file  
- Easy to deploy and run locally

## 📁 Folder Structure

chatbot/
├── static/
│ ├── styles.css
│ └── script.js
├── templates/
│ └── index.html
├── chat_history.json
├── app.py
├── .env
├── requirements.txt
└── README.md

bash
Copy
Edit

## ⚙️ Installation & Setup

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/chatbot.git
cd chatbot
Create a Virtual Environment

bash
Copy
Edit
python -m venv venv
venv\Scripts\activate       # For Windows
# OR
source venv/bin/activate    # For Linux/Mac
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Setup Environment Variables

Create a .env file in the root directory and add your API key:

ini
Copy
Edit
GEMINIAI_API_KEY=your_openai_api_key_here
Run the Flask App

bash
Copy
Edit
python app.py
Visit http://127.0.0.1:5000 in your browser to use the chatbot.

🧪 Testing
Start the server

Enter your question in the text box

Wait for the response from GeminiAI

The conversation will be saved in chat_history.json

📦 Dependencies
Flask

python-dotenv

Geminiai or google-generativeai (based on the version used)

All dependencies are listed in requirements.txt.

🛡️ Security Note
Make sure you never expose your .env file or API keys publicly on GitHub.
Use a .gitignore file to exclude .env from your commits.

🙋‍♀️ Author
Poojasri Bolisetti
GitHub Profile

📄 License
This project is open-source and available under the MIT License.
