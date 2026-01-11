import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def build_or_merge_passport(old_passport, messages):
    prompt = f"""
Ты профессиональный психолог.

ЗАДАЧА:
1. Если старого портрета нет — создай новый
2. Если есть — ОБЪЕДИНИ его с новыми сообщениями
3. Определи, произошёл ли резкий психологический сдвиг
4. Если да — объясни причину
5. Оцени confidence (0..1)

Верни СТРОГО:

ПОРТРЕТ:
<текст>

CONFIDENCE:
<число>

SHIFT:
true/false

SHIFT_REASON:
<текст или null>

СТАРЫЙ ПОРТРЕТ:
{old_passport}

НОВЫЕ СООБЩЕНИЯ:
{messages}
"""
    return parse(model.generate_content(prompt).text)


def format_passport(text, mode):
    prompt = f"""
Отформатируй психологический портрет.

РЕЖИМ: {mode}

short:
- 5–7 пунктов
- кратко

deep:
- полный анализ
- советы по общению

ТЕКСТ:
{text}
"""
    return model.generate_content(prompt).text


def compatibility(p1, p2):
    prompt = f"""
Ты психолог.

Сравни двух людей.

Верни:

SCORE:
<0..100>

SUMMARY:
<кратко>

RISKS:
<риски>

TIPS:
<советы>

ПОРТРЕТ 1:
{p1}

ПОРТРЕТ 2:
{p2}
"""
    return model.generate_content(prompt).text


def parse(text):
    result = {
        "text": "",
        "confidence": 0.0,
        "shift": {"detected": False, "reason": None}
    }

    current = None
    for line in text.splitlines():
        line = line.strip()
        if line == "ПОРТРЕТ:":
            current = "text"; continue
        if line == "CONFIDENCE:":
            current = "confidence"; continue
        if line == "SHIFT:":
            current = "shift"; continue
        if line == "SHIFT_REASON:":
            current = "reason"; continue

        if current == "text":
            result["text"] += line + "\n"
        elif current == "confidence":
            try: result["confidence"] = float(line)
            except: pass
        elif current == "shift":
            result["shift"]["detected"] = line.lower() == "true"
        elif current == "reason":
            result["shift"]["reason"] = None if line == "null" else line

    return result