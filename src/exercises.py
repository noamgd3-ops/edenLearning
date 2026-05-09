import random

# כל פועל מקבל אחד מששת המצבים:
# 1. עברית → איית הווה באנגלית
# 2. הווה → איית עבר
# 3. עבר → איית הווה
# 4. הווה → כתוב פירוש בעברית
# 5. עבר → כתוב פירוש בעברית
# 6. השלם משפט בעבר

MODES = ["heb_to_inf", "inf_to_past", "past_to_inf", "inf_to_hebrew", "past_to_hebrew", "fill_blank"]

FILL_TEMPLATES = [
    "Yesterday I ___ [hint].",
    "Last week she ___ [hint].",
    "They ___ [hint] last year.",
    "He ___ [hint] this morning.",
    "We ___ [hint] together.",
    "Last night she ___ [hint].",
    "Two days ago they ___ [hint].",
    "He ___ [hint] when he was young.",
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
    elif mode == "inf_to_hebrew":
        return {
            "mode": mode,
            "prompt": f"מה הפירוש בעברית של:  **{inf}**",
            "answer": heb,
            "hint": f"עבר: {past}",
        }
    elif mode == "past_to_hebrew":
        return {
            "mode": mode,
            "prompt": f"מה הפירוש בעברית של:  **{past}**",
            "answer": heb_past,
            "hint": f"שם פועל: {inf} ({heb})",
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
