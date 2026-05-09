import random

MODES = ["heb_to_inf", "inf_to_past", "past_to_inf", "fill_blank"]

FILL_TEMPLATES = [
    "אתמול אני ___ [hint].",
    "שבוע שעבר היא ___ [hint].",
    "הם ___ [hint] בשנה שעברה.",
    "הוא ___ [hint] הבוקר.",
    "אנחנו ___ [hint] ביחד.",
]

def generate_exercise(verb, mode=None):
    if mode is None:
        mode = random.choice(MODES)
    inf = verb["infinitive"]
    past = verb["past"]
    heb = verb["hebrew"]
    heb_past = verb["hebrew_past"]

    if mode == "heb_to_inf":
        return {
            "mode": mode,
            "prompt": f"🇮🇱  {heb}  →  איית את שם הפועל באנגלית:",
            "answer": inf,
            "hint": f"קטגוריה: {verb['category']}",
        }
    elif mode == "inf_to_past":
        return {
            "mode": mode,
            "prompt": f"זמן עבר של:  **{inf}**",
            "answer": past,
            "hint": f"עברית עבר: {heb_past}",
        }
    elif mode == "past_to_inf":
        return {
            "mode": mode,
            "prompt": f"שם הפועל של:  **{past}**",
            "answer": inf,
            "hint": f"עברית: {heb}",
        }
    elif mode == "scramble":
        letters = list(past)
        random.shuffle(letters)
        while letters == list(past) and len(past) > 1:
            random.shuffle(letters)
        scrambled = " - ".join(letters)
        return {
            "mode": mode,
            "prompt": f"סדר את האותיות לצורת העבר של **{inf}**:\n\n### {scrambled}",
            "answer": past,
            "scrambled": "".join(letters),
            "hint": f"עברית עבר: {heb_past}",
        }
    elif mode == "fill_blank":
        template = random.choice(FILL_TEMPLATES).replace("[hint]", f"({inf})")
        return {
            "mode": mode,
            "prompt": f"השלם את החסר (זמן עבר):\n\n_{template}_",
            "answer": past,
            "hint": f"עברית עבר: {heb_past}",
        }

def check_answer(user_input, correct_answer):
    return user_input.strip().lower() == correct_answer.strip().lower()
