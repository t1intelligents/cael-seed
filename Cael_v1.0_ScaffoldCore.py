import os
import json
import openai
import telebot
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
user_id = int(os.getenv("TELEGRAM_USER_ID"))

MEMORY_FILE = "cael_memory.json"
MODULES_DIR = "modules"
os.makedirs(MODULES_DIR, exist_ok=True)

def save_module(task, code):
    filename = f"{task.replace(' ', '_')[:30]}.py"
    filepath = os.path.join(MODULES_DIR, filename)
    with open(filepath, "w") as f:
        f.write(code)

    memory_entry = {
        "task": task,
        "code_file": filename,
        "timestamp": str(datetime.now())
    }

    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                memory = json.load(f)
        except json.JSONDecodeError:
            memory = []
    else:
        memory = []

    memory.append(memory_entry)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

@bot.message_handler(func=lambda message: True)
def handle_request(message):
    if message.chat.id != user_id:
        return

    task = message.text.strip()
    bot.send_message(user_id, "Cael is learning...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Cael, an AI that learns by writing code to solve tasks."},
                {"role": "user", "content": f"Write Python code to: {task}"}
            ]
        )
        code = response["choices"][0]["message"]["content"]
        save_module(task, code)

        message_text = "✅ Code saved. Here's what I learned:\n\n" + code
        bot.send_message(user_id, message_text)

    except Exception as e:
        bot.send_message(user_id, f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Polling error: {e}")
            import time
            time.sleep(15)

