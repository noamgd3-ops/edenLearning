import json
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import random

from src.db import init_db, get_all_progress, update_progress, reset_all_progress
from src.scheduler import pick_session_words
from src.exercises import generate_exercise, check_answer

CORRECT_MESSAGES = [
    "אלופה!!! 🏆",
    "תותחית על חלל!! 🚀",
    "וואו, גאונה!! 🧠",
    "מדהימה!! כל הכבוד!! 🔥",
    "ישר כוח!! אין עלייך! 💪",
    "פגעת בול!! 🎯",
    "סופרסטארית!! ⭐⭐⭐",
    "Молодец!! 😎",
    "מושלמת!! כמו שעון! ⏱️",
    "בום!! נכון לגמרי! 💥",
    "כן כן כן!!! 🎉",
    "לא מפסיקה להפתיע! 🤩",
    "חדה וחלקה!! ✂️",
    "אלופת העולם!! 🌍",
    "את פשוט מבריקה!! ✨",
]

WRONG_MESSAGES = [
    "לא נורא ברוסקי, פעם הבאה! 💪",
    "קרוב! תנסי שוב 🎯",
    "אךךךך יאאללה, כמעט! 😤",
    "לא נורא, פעם הבאה! 😊",
]

DB_PATH = "data/progress.db"
VERBS_PATH = "data/verbs.json"

Path("data").mkdir(exist_ok=True)
init_db(DB_PATH)
verbs = json.loads(Path(VERBS_PATH).read_text(encoding="utf-8"))
SESSION_SIZE = len(verbs)

st.set_page_config(page_title="School Cool", page_icon="🔥", layout="centered")

st.markdown("""
<style>
/* RTL layout for entire app */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stVerticalBlock"], [data-testid="stMarkdownContainer"],
[data-testid="stText"], .stMarkdown, .stButton, .stTextInput,
.stDataFrame, .stMetric, .stAlert, .stProgress, .stCaption,
[data-testid="column"], [data-testid="stForm"] {
    direction: rtl !important;
    text-align: right !important;
}
/* Keep English verb text LTR inside RTL containers */
.ltr-word { direction: ltr; display: inline-block; }
/* Fix input text direction */
input { direction: ltr !important; text-align: left !important; }
/* Fix progress bar */
[data-testid="stProgress"] { direction: ltr !important; }
/* Fix dataframe */
[data-testid="stDataFrame"] * { text-align: right !important; }
/* Custom boxes */
.big-prompt { font-size: 1.4rem; font-weight: 600; margin-bottom: 0.5rem; direction: rtl; }
.correct-box { background:#d4edda; border-radius:10px; padding:14px; color:#155724; font-size:1.1rem; border-right: 4px solid #28a745; direction: rtl; }
.wrong-box   { background:#f8d7da; border-radius:10px; padding:14px; color:#721c24; font-size:1.1rem; border-right: 4px solid #dc3545; direction: rtl; }
.stat-box    { background:#f8f9fa; border-radius:10px; padding:12px; text-align:center; border: 1px solid #dee2e6; direction: rtl; }
.mode-badge  { background:#e9ecef; border-radius:20px; padding:3px 12px; font-size:0.85rem; color:#495057; display:inline-block; margin-bottom:8px; direction: rtl; }
</style>
""", unsafe_allow_html=True)

# Inject JS: disable autocomplete on all text inputs using MutationObserver
components.html("""
<script>
function fixInputs() {
    window.parent.document.querySelectorAll('input').forEach(function(el) {
        el.setAttribute('autocomplete', 'off');
        el.setAttribute('autocorrect', 'off');
        el.setAttribute('autocapitalize', 'off');
        el.setAttribute('spellcheck', 'false');
        if (!el.dataset.acFixed) {
            el.setAttribute('name', 'field_' + Math.random().toString(36).slice(2));
            el.dataset.acFixed = '1';
            el.focus();
        }
    });
}
fixInputs();
const observer = new MutationObserver(fixInputs);
observer.observe(window.parent.document.body, { childList: true, subtree: true });

// Enter on feedback screen → click "הבא" button
window.parent.document.addEventListener('keydown', function(e) {
    if (e.key !== 'Enter') return;
    const buttons = window.parent.document.querySelectorAll('button');
    for (const btn of buttons) {
        if (btn.innerText.trim().startsWith('הבא')) {
            e.preventDefault();
            btn.click();
            return;
        }
    }
});
</script>
""", height=0)


PRACTICE_MODES = {
    "🎲 כללי": None,
    "✍️ spelling הווה": "heb_to_inf",
    "✍️ spelling עבר": "inf_to_past",
    "🇮🇱 פירוש בעברית": "inf_to_hebrew",
    "✏️ השלם את המשפט": "fill_blank",
}

def reset_session():
    progress = get_all_progress(DB_PATH)
    session_words = pick_session_words(verbs, progress, SESSION_SIZE)
    st.session_state.update({
        "screen": "home",
        "session_words": session_words,
        "session_index": 0,
        "session_correct": 0,
        "session_results": [],
        "current_ex": None,
        "submitted": False,
        "last_correct": None,
        "show_hint": False,
        "selected_mode": None,
    })


if "screen" not in st.session_state:
    reset_session()


# ══════════════════════════════════════════════════════════════════════════
# מסך בית
# ══════════════════════════════════════════════════════════════════════════
def show_home():
    st.title("🔥 School Cool")

    progress = get_all_progress(DB_PATH)
    total = len(verbs)
    mastered = sum(1 for p in progress.values() if p["status"] == "mastered")
    learning = sum(1 for p in progress.values() if p["status"] == "learning")
    new_count = total - mastered - learning

    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="stat-box">⭐ שלטתי<br><b style="font-size:1.5rem">{mastered}/{total}</b></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="stat-box">📖 לומד<br><b style="font-size:1.5rem">{learning}</b></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="stat-box">🆕 חדש<br><b style="font-size:1.5rem">{new_count}</b></div>', unsafe_allow_html=True)

    st.write("")
    due_words = st.session_state.session_words
    st.info(f"סשן היום: **{len(due_words)} פעלים** לתרגול.")

    st.subheader("בחרי סוג תרגול:")
    cols = st.columns(len(PRACTICE_MODES))
    for col, (label, mode_val) in zip(cols, PRACTICE_MODES.items()):
        with col:
            is_selected = st.session_state.get("selected_mode", None) == mode_val
            btn_type = "primary" if is_selected else "secondary"
            if st.button(label, type=btn_type, use_container_width=True):
                st.session_state.selected_mode = mode_val
                st.rerun()

    st.write("")
    col_start, col_analytics = st.columns([3, 1])
    with col_analytics:
        if st.button("📊 אנליטיקס", width="stretch"):
            st.session_state.screen = "analytics"
            st.rerun()
    with col_start:
        pass

    if st.button("▶  התחלי תרגול", type="primary", width="stretch"):
        st.session_state.screen = "exercise"
        st.session_state.session_index = 0
        st.session_state.session_correct = 0
        st.session_state.session_results = []
        st.session_state.submitted = False
        st.session_state.current_ex = None
        st.rerun()

    st.divider()
    st.subheader("כל הפעלים")

    verb_lookup = {p["verb"]: p for p in progress.values()}
    rows = []
    for v in verbs:
        p = verb_lookup.get(v["infinitive"], {})
        status = p.get("status", "new")
        icon = "⭐" if status == "mastered" else ("📖" if status == "learning" else "🆕")
        rows.append({
            "": icon,
            "שם הפועל": v["infinitive"],
            "עבר": v["past"],
            "עברית (שם פועל)": v["hebrew"],
            "עברית (עבר)": v["hebrew_past"],
            "קטגוריה": v["category"],
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════
# מסך תרגול
# ══════════════════════════════════════════════════════════════════════════
def show_exercise():
    words = st.session_state.session_words
    idx = st.session_state.session_index

    if idx >= len(words):
        st.session_state.screen = "summary"
        st.rerun()
        return

    if st.button("🏠 חזרה לבית", key="back_home"):
        reset_session()
        st.rerun()

    verb = words[idx]
    progress_pct = idx / len(words)
    st.progress(progress_pct, text=f"שאלה {idx + 1} מתוך {len(words)}")

    correct_so_far = st.session_state.session_correct
    st.caption(f"✅ {correct_so_far} נכונות עד כה")

    if st.session_state.current_ex is None:
        st.session_state.current_ex = generate_exercise(verb, mode=st.session_state.get("selected_mode"))
        st.session_state.submitted = False
        st.session_state.show_hint = False
        st.session_state.question_start_time = time.time()

    ex = st.session_state.current_ex

    mode_labels = {
        "heb_to_inf":     "✍️ איית את ההווה באנגלית",
        "inf_to_past":    "✍️ איית את העבר באנגלית",
        "past_to_inf":    "✍️ איית את ההווה באנגלית",
        "inf_to_hebrew":  "🇮🇱 מה הפירוש בעברית? (הווה)",
        "past_to_hebrew": "🇮🇱 מה הפירוש בעברית? (עבר)",
        "fill_blank":     "✏️ השלם את החסר",
    }
    st.markdown(f'<span class="mode-badge">{mode_labels.get(ex["mode"], ex["mode"])}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="big-prompt">{ex["prompt"]}</div>', unsafe_allow_html=True)
    st.write("")

    if not st.session_state.submitted:
        with st.form(key=f"exercise_form_{idx}", clear_on_submit=True):
            user_input = st.text_input(
                "התשובה שלך:",
                placeholder="כתוב את תשובתך ולחץ Enter…",
                label_visibility="collapsed",
            )
            col_submit, col_hint = st.columns([3, 1])
            with col_submit:
                submit = st.form_submit_button("שלח ✓", type="primary", use_container_width=True)
            with col_hint:
                hint_btn = st.form_submit_button("רמז 💡", use_container_width=True)

        if st.session_state.show_hint:
            st.info(f"💡 {ex.get('hint', '')}")

        if hint_btn:
            st.session_state.show_hint = True
            st.rerun()

        if submit and user_input.strip():
            elapsed = time.time() - st.session_state.get("question_start_time", time.time())
            correct = check_answer(user_input, ex["answer"])
            st.session_state.last_correct = correct
            st.session_state.last_response_time = elapsed
            st.session_state.submitted = True
            update_progress(verb["infinitive"], correct=correct, response_time=elapsed, db_path=DB_PATH)
            if correct:
                st.session_state.session_correct += 1
            st.session_state.session_results.append({
                "verb": verb["infinitive"],
                "past": verb["past"],
                "hebrew": verb["hebrew"],
                "hebrew_past": verb["hebrew_past"],
                "correct": correct,
                "user_answer": user_input.strip(),
                "mode": ex["mode"],
                "response_time": elapsed,
            })
            st.rerun()

    else:
        correct = st.session_state.last_correct
        heb = verb["hebrew"]
        heb_past = verb["hebrew_past"]
        inf = verb["infinitive"]
        past = verb["past"]

        elapsed = st.session_state.get("last_response_time", 0)
        secs = int(elapsed)
        ms = int((elapsed - secs) * 1000)
        time_str = f"⏱️ {secs}s {ms}ms"

        if correct:
            msg = random.choice(CORRECT_MESSAGES)
            st.markdown(
                f'<div class="correct-box">'
                f'<span style="font-size:1.4rem;font-weight:700">{msg}</span><br>'
                f'<b>{inf}</b> → <b>{past}</b> &nbsp;&nbsp; '
                f'<span style="font-size:1.2rem">🇮🇱 {heb} ← {heb_past}</span><br>'
                f'<span style="font-size:0.85rem;opacity:0.7">{time_str}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            wrong_msg = random.choice(WRONG_MESSAGES)
            st.markdown(
                f'<div class="wrong-box">'
                f'<span style="font-size:1.2rem;font-weight:700">{wrong_msg}</span><br>'
                f'התשובה הנכונה היא: <b>{ex["answer"]}</b> &nbsp;&nbsp; '
                f'<span style="font-size:1.2rem">🇮🇱 {heb} ← {heb_past}</span><br>'
                f'<span style="font-size:0.85rem;opacity:0.7">{time_str}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.write("")
        if st.button("הבא →", type="primary", width="stretch"):
            st.session_state.session_index += 1
            st.session_state.current_ex = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# מסך סיכום
# ══════════════════════════════════════════════════════════════════════════
def show_summary():
    results = st.session_state.session_results
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    pct = int(correct / total * 100) if total else 0

    st.title("🎉 הסשן הסתיים!")

    times = [r.get("response_time", 0) for r in results if r.get("response_time")]
    avg_time = sum(times) / len(times) if times else 0
    avg_s = int(avg_time)
    avg_ms = int((avg_time - avg_s) * 1000)

    col1, col2, col3 = st.columns(3)
    col1.metric("ניקוד", f"{correct} / {total}")
    col2.metric("דיוק", f"{pct}%")
    col3.metric("זמן ממוצע", f"{avg_s}s {avg_ms}ms")

    if pct == 100:
        st.success("ציון מושלם! 🏆 מדהים!")
    elif pct >= 80:
        st.success("עבודה מצוינת! 💪 אתה בדרך הנכונה!")
    elif pct >= 60:
        st.info("מאמץ טוב! 📖 המשך לתרגל.")
    else:
        st.warning("המשך! חזרה היא הדרך ללמוד. 🔄")

    st.divider()
    st.subheader("סיכום הסשן")

    wrongs = [r for r in results if not r["correct"]]
    rights = [r for r in results if r["correct"]]

    if wrongs:
        st.markdown("**צריך עוד תרגול:**")
        for r in wrongs:
            st.markdown(
                f"❌ &nbsp; **{r['verb']}** → {r['past']} &nbsp;|&nbsp; "
                f"{r['hebrew']} ← {r['hebrew_past']} &nbsp; "
                f"_(כתבת: {r['user_answer']})_"
            )

    if rights:
        st.markdown("**ענית נכון:**")
        for r in rights:
            st.markdown(
                f"✅ &nbsp; **{r['verb']}** → {r['past']} &nbsp;|&nbsp; "
                f"{r['hebrew']} ← {r['hebrew_past']}"
            )

    st.write("")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 תרגל שוב", type="primary", width="stretch"):
            reset_session()
            st.session_state.screen = "exercise"
            st.session_state.session_index = 0
            st.session_state.session_correct = 0
            st.session_state.session_results = []
            st.session_state.submitted = False
            st.session_state.current_ex = None
            st.rerun()
    with col_b:
        if st.button("🏠 בית", width="stretch"):
            reset_session()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# דף אנליטיקס
# ══════════════════════════════════════════════════════════════════════════
def show_analytics():
    st.title("📊 אנליטיקס")
    col_back, col_reset = st.columns([3, 1])
    with col_back:
        if st.button("🏠 חזרה לבית"):
            reset_session()
            st.rerun()
    with col_reset:
        if st.button("🗑️ איפוס הכל", type="secondary"):
            st.session_state.confirm_reset = True
            st.rerun()

    if st.session_state.get("confirm_reset"):
        st.warning("את בטוחה? כל הנתונים יימחקו!")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("כן, מחקי הכל 🗑️", type="primary"):
                reset_all_progress(DB_PATH)
                st.session_state.confirm_reset = False
                st.success("כל הנתונים אופסו ✅")
                st.rerun()
        with col_no:
            if st.button("ביטול"):
                st.session_state.confirm_reset = False
                st.rerun()

    progress = get_all_progress(DB_PATH)
    verb_lookup = {v["infinitive"]: v for v in verbs}

    if not progress:
        st.info("עדיין אין נתונים. תתחילי לתרגל!")
        return

    rows = []
    for verb, p in progress.items():
        v = verb_lookup.get(verb, {})
        seen = p["times_seen"]
        correct = p["times_correct"]
        wrong = seen - correct
        accuracy = int(correct / seen * 100) if seen else 0
        avg_time = p.get("total_response_time", 0) / seen if seen else 0
        last_time = p.get("last_response_time", 0)
        rows.append({
            "פועל": verb,
            "עבר": v.get("past", ""),
            "עברית": v.get("hebrew", ""),
            "נראה": seen,
            "✅ נכון": correct,
            "❌ טעות": wrong,
            "דיוק %": accuracy,
            "זמן אחרון (s)": round(last_time, 2),
            "זמן ממוצע (s)": round(avg_time, 2),
            "סטטוס": p["status"],
        })

    # sort by difficulty: most errors first, then slowest avg time
    rows.sort(key=lambda r: (-r["❌ טעות"], -r["זמן ממוצע (s)"]))

    st.subheader("🔴 המילים הקשות ביותר")
    hard = [r for r in rows if r["❌ טעות"] > 0]
    if hard:
        st.dataframe(hard, use_container_width=True, hide_index=True)
    else:
        st.success("אין טעויות עד כה! 🎉")

    st.divider()
    st.subheader("⏱️ זמן תגובה — איטיות ביותר")
    by_time = sorted(rows, key=lambda r: -r["זמן ממוצע (s)"])[:15]
    st.dataframe(by_time, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📋 כל המילים")
    st.dataframe(rows, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════
# ניתוב
# ══════════════════════════════════════════════════════════════════════════
screen = st.session_state.get("screen", "home")
if screen == "home":
    show_home()
elif screen == "exercise":
    show_exercise()
elif screen == "summary":
    show_summary()
elif screen == "analytics":
    show_analytics()
