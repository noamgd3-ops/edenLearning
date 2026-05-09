import random
from datetime import date

def pick_session_words(verbs, progress, session_size=20):
    today = date.today().isoformat()
    due, new, mastered = [], [], []
    for v in verbs:
        p = progress.get(v["infinitive"])
        if p is None:
            new.append(v)
        elif p["status"] == "mastered":
            mastered.append(v)
        elif p["next_review"] <= today:
            due.append(v)
        else:
            new.append(v)
    random.shuffle(new)
    random.shuffle(mastered)
    pool = due + new + mastered
    return pool[:session_size]
