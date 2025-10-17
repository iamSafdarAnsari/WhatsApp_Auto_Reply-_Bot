import pyautogui
import time
import pyperclip
import re
import os
from openai import OpenAI

# ===============================
# CONFIGURATION SECTION
# ===============================

DRY_RUN = False  # True = test mode (won’t send messages)
TARGET_SENDER = "Zoya"

# Screen coordinates (adjust for your screen)
CHAT_SELECT_X1, CHAT_SELECT_Y1 = 1104, 303
CHAT_SELECT_X2, CHAT_SELECT_Y2 = 1603, 1455
MESSAGE_BOX_X, MESSAGE_BOX_Y = 1312, 1439  # where message is typed
CHROME_ICON_X, CHROME_ICON_Y = 1580, 1563
MESSAGE_BOX_FOCUS_X, MESSAGE_BOX_FOCUS_Y = 1412, 600  # where to click after copy (to refocus WhatsApp)

# OpenAI setup
OPENAI_API_KEY = os.getenv(
    # "OPENAI_API_KEY", <Your OPENAI_API_KEY>
)
client = OpenAI(api_key=OPENAI_API_KEY)

pyautogui.FAILSAFE = True  # Move mouse to corner to abort safely


# ===============================
# HELPER FUNCTIONS
# ===============================

def countdown(seconds=5):
    """Small timer before bot starts."""
    print(f"Starting in {seconds} seconds. Move mouse to a corner to stop.")
    for i in range(seconds, 0, -1):
        print(f"{i}...")
        time.sleep(1)


def get_last_message(chat_history):
    """Extract the last message (timestamp, sender, message)."""
    if not chat_history:
        return None, None, None

    lines = [ln.strip() for ln in chat_history.splitlines() if ln.strip()]
    pattern = re.compile(r'^\[(.*?)\]\s*(.+?):\s*(.*)$')

    for ln in reversed(lines):
        match = pattern.match(ln)
        if match:
            timestamp, sender, message = match.groups()
            return timestamp, sender, message
    return None, None, None


def clean_ai_reply(reply_text):
    """Clean timestamps, names, and long replies."""
    reply_text = re.sub(r'^\[.*?\]\s*[A-Za-z ]*:\s*', '', reply_text).strip()
    sentences = re.split(r'[.!?]', reply_text)
    short_reply = '. '.join(sentences[:2]).strip()
    return short_reply[:120]  # keep short and natural


def generate_reply(chat_history):
    """Generate short, clean AI reply."""
    print("Generating AI reply...")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Safdar, a funny Indian coder who chats casually in Hinglish "
                    "(Hindi + English mix). "
                    "Read the chat and reply in one short, natural line — no timestamp, no name, "
                    "no emoji spam. Be witty or chill, like texting a friend."
                ),
            },
            {"role": "user", "content": chat_history},
        ],
    )
    reply = completion.choices[0].message.content.strip()
    return clean_ai_reply(reply)


def copy_chat_from_screen():
    """Always reselect and copy chat area from screen."""
    if not DRY_RUN:
        # Select chat area
        pyautogui.moveTo(CHAT_SELECT_X1, CHAT_SELECT_Y1)
        pyautogui.dragTo(CHAT_SELECT_X2, CHAT_SELECT_Y2, duration=1.5, button='left')
        # Copy selected text
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)
        # Click somewhere neutral to remove selection
        pyautogui.click(MESSAGE_BOX_FOCUS_X, MESSAGE_BOX_FOCUS_Y)
        time.sleep(0.5)
    return pyperclip.paste()


def send_message(message):
    """Paste and send message on WhatsApp."""
    if DRY_RUN:
        print(f"[DRY RUN] Would send: {message}")
        return
    pyautogui.click(MESSAGE_BOX_X, MESSAGE_BOX_Y)
    time.sleep(0.5)
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')


# ===============================
# MAIN LOOP
# ===============================

def main():
    countdown(5)
    print("🚀 WhatsApp Auto-Reply Bot Started...")

    if not DRY_RUN:
        try:
            pyautogui.click(CHROME_ICON_X, CHROME_ICON_Y)
        except Exception as e:
            print("⚠️ Could not click Chrome/WhatsApp:", e)

    last_message_seen = None

    while True:
        try:
            # Always reselect and copy chat every cycle
            chat_history = copy_chat_from_screen()
            ts, sender, message = get_last_message(chat_history)

            if not message or message == last_message_seen:
                time.sleep(3)
                continue

            last_message_seen = message
            print(f"\n📩 New message from {sender}: {message}")

            if sender == TARGET_SENDER:
                reply = generate_reply(chat_history)
                print("✅ Sending short reply:", reply)
                send_message(reply)
            else:
                print("⏸ Ignoring message (not from target contact).")

            # Short wait before rechecking chat
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped manually.")
            break
        except Exception as e:
            print("⚠️ Error during loop:", e)
            time.sleep(5)


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    main()
