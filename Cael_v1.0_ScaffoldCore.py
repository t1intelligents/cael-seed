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

# Memory and mode files
MEMORY_FILE = "cael_memory.json"
MODE_FILE = "cael_mode.json"
default_mode = {"mode": "chat"}

# Initialize memory and mode files
for file_name, default_content in [(MEMORY_FILE, []), (MODE_FILE, default_mode)]:
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            json.dump(default_content, f)

# Load mode
def get_mode():
    with open(MODE_FILE, "r") as f:
        return json.load(f).get("mode", "chat")

def set_mode(new_mode):
    with open(MODE_FILE, "w") as f:
        json.dump({"mode": new_mode}, f)

# Save code to memory
def save_code_to_memory(code_snippet):
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
        memory.append(code_snippet)
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"Error saving code to memory: {e}")

# Extract code block from response
def extract_code_block(response):
    parts = response.split("```")
    return parts[1].strip() if len(parts) > 1 else None

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

    try:
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
                reply = f"✅ Code saved. Here's what I learned:\n\n{reply}"
            elif "def " in reply or "class " in reply:
                save_code_to_memory(reply)
                reply = f"✅ Code saved (no block detected). Here's what I learned:\n\n{reply}"
            else:
                reply = f"⚠️ No valid code detected to save.\n\n{reply}"

        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# Start polling
print("🤖 Cael is alive and listening...")
while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Polling error: {e}")
        import time
        time.sleep(15)
