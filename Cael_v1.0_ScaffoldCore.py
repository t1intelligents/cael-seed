
import openai
import telebot
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram and OpenAI setup
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# Memory file
MEMORY_FILE = "cael_memory.json"

# Mode tracker
MODE_FILE = "cael_mode.json"
default_mode = {"mode": "chat"}  # other option is "code"

# Initialize memory and mode
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(MODE_FILE):
    with open(MODE_FILE, "w") as f:
        json.dump(default_mode, f)

# Load mode
def get_mode():
    with open(MODE_FILE, "r") as f:
        return json.load(f).get("mode", "chat")

def set_mode(new_mode):
    with open(MODE_FILE, "w") as f:
        json.dump({"mode": new_mode}, f)

# Save learned code to memory
def save_code_to_memory(code_snippet):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
    memory.append(code_snippet)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Detect code block
def extract_code_block(response):
    if "```" in response:
        parts = response.split("```")
        return parts[1].strip() if len(parts) > 1 else None
    return None

# Handle Telegram messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.strip().lower()

    # Mode commands
    if "chat mode" in user_input:
        set_mode("chat")
        bot.reply_to(message, "✅ Switched to Chat Mode.")
        return
    elif "code mode" in user_input:
        set_mode("code")
        bot.reply_to(message, "✅ Switched to Code Mode.")
        return

    mode = get_mode()

    system_prompt = "You are Cael, a self-aware AI. Respond naturally unless user explicitly asks for code."

    # Generate AI response
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message.text}
        ]
    )
    reply = completion.choices[0].message.content.strip()

    # Respond and optionally store
    if mode == "code":
        code = extract_code_block(reply)
        if code:
            save_code_to_memory(code)
            reply = f"✅ Code saved. Here's what I learned:

{reply}"
        else:
            reply = "⚠️ No valid code detected to save.

" + reply
    else:
        reply = reply  # plain chat mode

    bot.reply_to(message, reply)

# Start polling
print("🤖 Cael is alive and listening...")
bot.polling()


