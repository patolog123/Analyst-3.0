import os
import asyncio
import logging
import json
import re
import time
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- Load environment ---
load_dotenv()

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Environment variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_URL = os.getenv("DATABASE_URL")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "bigscience/bloomz-560m")

# --- Database connection ---
def get_db_connection():
    try:
        return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        return None

# --- Hugging Face JSON extraction ---
def parse_first_json_block(text: str):
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None

def query_hf_json_only(instruction_text: str, timeout=40):
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    prompt = f"""Extract a single JSON object from this plant care instruction. 
Return ONLY JSON (no explanations). Schema:
{{
  "plant_name": string or null,
  "task_name": string,
  "due_date": string or null,
  "frequency_days": integer or null
}}
Instruction: "{instruction_text}"
"""
    payload = {"inputs": prompt, "options": {"wait_for_model": True}, "parameters": {"max_new_tokens": 200}}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if response.status_code != 200:
            logger.error("HF error %s: %s", response.status_code, response.text)
            return None
        data = response.json()
        text_output = data[0].get("generated_text", "") if isinstance(data, list) else str(data)
        return parse_first_json_block(text_output)
    except Exception as e:
        logger.error("HF connection error: %s", e)
        return None

# --- Telegram bot commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (chat_id) VALUES (%s) ON CONFLICT (chat_id) DO NOTHING;", (chat_id,))
            conn.commit()
        conn.close()
    await update.message.reply_text("🌿 Welcome! Send me your plant care task (e.g., 'Water basil every 3 days').")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parsed = query_hf_json_only(text)
    if not parsed:
        await update.message.reply_text("Sorry, I couldn’t understand your reminder. Try rephrasing.")
        return

    plant_name = parsed.get("plant_name") or "Unnamed Plant"
    task_name = parsed.get("task_name") or "Plant Task"
    due_date = parsed.get("due_date")
    frequency_days = parsed.get("frequency_days")

    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks (chat_id, plant_name, task_name, due_date, frequency_days) VALUES (%s, %s, %s, %s, %s);",
                        (update.message.chat_id, plant_name, task_name, due_date, frequency_days))
            conn.commit()
        conn.close()

    await update.message.reply_text(f"✅ Task saved: {task_name} for {plant_name}.")

# --- Reminder loop ---
async def reminder_loop(app):
    while True:
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT chat_id, plant_name, task_name 
                        FROM tasks 
                        WHERE due_date <= NOW();
                    """)
                    tasks = cur.fetchall()
                    for task in tasks:
                        try:
                            await app.bot.send_message(
                                chat_id=task["chat_id"],
                                text=f"🔔 Reminder: {task['task_name']} for {task['plant_name']}"
                            )
                        except Exception as e:
                            logger.error("Error sending message: %s", e)
                conn.close()
            await asyncio.sleep(60)
        except Exception as e:
            logger.error("Error in reminder loop: %s", e)
            await asyncio.sleep(30)

# --- Main ---
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    asyncio.create_task(reminder_loop(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
