from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import asyncio
import os

# Telethon imports
from telethon import TelegramClient, events

# Application-specific imports
from backend.Agents.orchestrator import NewsOrchestrator
from backend.Agents.Foundations.OpenAIAPI import OpenAIAPI
from backend.API.AppData import AppData
from backend.Agents.Foundations.XDigest import TwikitAPI
from backend.Agents.prompts import FOLLOW_UP_PROMPT

# ======================================
# Flask Configuration and Initialization
# ======================================
class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 8000))

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# This function is used to emit new data to the client
def emit_data(socketio, new_data):
    socketio.emit('client_comms', {'data': new_data})

AppData.data["emit_function"] = emit_data
AppData.data["socketio"] = socketio

@app.route("/")
def hello_world():
    return "Kraken."

@socketio.on('connect')
def test_connect(auth):
    print("Client Connected")
    emit('my response', {'data': 'Connected'})

@socketio.on('gen_daily')
def generate_daily_krakbit():
    thread = threading.Thread(target=run_async_daily_krakbit)
    thread.daemon = True
    thread.start()
    return jsonify({"message": "gen_started"}), 200

@socketio.on('gen_question')
def generate_question_krakbit(data):
    query = data.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    thread = threading.Thread(target=run_async_daily_krakbit, args=(query,))
    thread.daemon = True
    thread.start()
    return jsonify({"message": "gen_started"}), 200

@app.route("/get_x_trending")
async def get_x_trending():
    twitter = TwikitAPI()
    data = await twitter.request_and_return_top_crypto()
    return_data = []
    for tweet in data:
        return_data.append({
            'id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at if tweet.created_at else None,
            'user_name': tweet.user.name,
            'user_screen_name': tweet.user.screen_name,
            'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
        })
    return jsonify({"posts": return_data}), 200

@app.route("/ask_question", methods=["GET", "POST"])
async def ask_question():
    json_data = request.get_json()
    content = json_data["content"]
    question = json_data["question"]
    openai_api = OpenAIAPI()
    prompt = FOLLOW_UP_PROMPT.format(
        news=content,
        question=question
    )
    system_prompt = "You are an AI assistant tasked with answering user questions"
    response = await openai_api.query_chatgpt(
        system_prompt=system_prompt,
        user_prompt=prompt,
        model="gpt-4o",
        temperature=0.2  # Low temp for deterministic index selection
    )
    return jsonify({"response": response}), 200

def run_async_daily_krakbit(topic=None):
    # Execute the async helper in its own event loop
    asyncio.run(daily_krakbit_helper(topic))

async def daily_krakbit_helper(topic=None):
    try:
        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": "Connecting to Server"})
        orchestrator = NewsOrchestrator()
        print("\nStarting Generic News Generation...")
        # Generate news and save it in business_news
        business_news = await orchestrator.generate_generic_news(topic="business", focus=topic)
        print("✅ Generated News:", business_news)
        return business_news  # Return the generated news for further processing
    except Exception as e:
        print(f"\nAn error occurred during the example run: {e}")
        import traceback
        traceback.print_exc()
        return None

# ======================================
# Telethon Integration
# ======================================
# Your Telegram API credentials from my.telegram.org
api_id = 23466168
api_hash = '20c65e528f26ceba3eb4b8450dff6296'
bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'  # Replace with your bot token

client = TelegramClient('anon', api_id, api_hash)

@client.on(events.NewMessage)
async def telegram_handler(event):
    msg = event.raw_text.strip().lower()
    # When a "news" message is received, reply and run the news generation function.
    if msg == "news":
        print("🟢 Telegram: 'news' message received.")
        await event.reply("⏳ Generating news...")
        
        generated_data = await daily_krakbit_helper()  # Now works with the default parameter
        
        # Build the response message using the generated data
        total_message = ""
        if generated_data:
            for article in generated_data:
                if "headline" in article:
                    if total_message:
                        total_message += "\n\n"
                    total_message += f"📰 **{article['headline']}**\n\n"
                    total_message += f"{article['content']}\n\n"
                    total_message += f"Read More: {article['web_url']}"
        else:
            total_message = "No news generated."

        await event.reply("✅ News generation complete!")
        await event.reply(total_message)

def start_telegram_bot():
    # Create a new event loop for this thread and set it as current
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start the client (use bot_token=bot_token if using a bot token)
    # client.start(bot_token=bot_token)  # or client.start() if using user account auth
    client.start()
    print("✅ Telegram bot running.")
    client.run_until_disconnected()


# ======================================
# Main: Start Flask & Telethon
# ======================================
if __name__ == "__main__":
    # Launch Telegram bot in a background thread so it runs concurrently with Flask.
    telegram_thread = threading.Thread(target=start_telegram_bot)
    telegram_thread.daemon = True
    telegram_thread.start()

    # Run the Flask app (via SocketIO)
    socketio.run(app,
                 host=app.config['HOST'],
                 port=app.config['PORT'],
                 debug=True)