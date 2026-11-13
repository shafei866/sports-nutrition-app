import streamlit as st
from groq import Groq
from google import genai
from google.genai import types

st.set_page_config(page_title="Student Athlete Nutrition Coach", page_icon="💪", layout="wide")

GROQ_MODELS = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]  # primary (higher free limits)
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-3.5-flash"]  # fallback if Groq fails or hits its limit

# ───────────────────────── Translations ─────────────────────────
TEXT = {
    "en": {
        "page_title": "Student Athlete Nutrition Coach",
        "hero_sub": "Smart nutrition, hydration and myth-busting for athletes who study.",
        "sidebar_header": "🎛️ Your details",
        "weight": "Weight (kg)",
        "goal": "Goal",
        "sport": "Sport",
        "schedule": "Training time",
        "disclaimer": "⚠️ Results are general guidance, not a substitute for a dietitian or doctor.",
        "goals": {"muscle": "💪 Build muscle", "fat": "🔥 Burn fat", "focus": "⚡ Energy & focus"},
        "sports": {"gym": "🏋️ Gym", "football": "⚽ Football", "running": "🏃 Running"},
        "schedules": {"before": "🌅 Before classes", "after": "🌇 After classes", "between": "🕑 Between classes"},
        "tabs": ["🍽️ Macros & Plate", "🎒 Lunch Box & Workout", "🕵️ Myth Buster", "💧 Hydration"],
        "t1_sub": "Your approximate daily needs",
        "calories": "Calories",
        "protein": "Protein",
        "carbs": "Carbs",
        "fat_m": "Fat",
        "g": "g",
        "split": "Where your calories come from",
        "t1_caption": "Estimates based on your weight, goal and sport.",
        "t1_btn": "🤖 Suggest a balanced daily plate",
        "t2_sub": "Which situation are you in right now?",
        "situations": {
            "pre1": "🚶 Heading to campus, training in 1 hour",
            "pre3": "⏳ Training in 3 hours",
            "post": "😮‍💨 Just finished training, feeling exhausted",
            "lunchbox": "🎒 Need a lunch box for the whole day",
        },
        "avoid": "Foods you avoid or are allergic to (optional)",
        "t2_btn": "🤖 Suggest meals",
        "t3_sub": "Heard a gym myth? Ask here",
        "ex1": "Do I need protein powder and creatine to build a good physique?",
        "ex2": "Does fasted morning training burn fat faster?",
        "chat_ph": "Ask about any gym myth or nutrition question...",
        "chat_hint": "Each question is answered on its own.",
        "clear": "🗑️ Clear chat",
        "t4_sub": "Hydration calculator",
        "hours": "Training hours today",
        "intake": "Liters you drink per day (roughly)",
        "target": "Daily target",
        "gap": "Still to drink",
        "progress": "Today's water progress",
        "liters": "L",
        "h_err": "🚨 You're drinking far less than you need. Dehydration reduces focus and performance.",
        "h_warn": "⚠️ You should drink a bit more water.",
        "h_over": "⚠️ Drinking too much water at once can upset your electrolyte balance. Spread it through the day.",
        "h_ok": "✅ Good amount.",
        "h_salts": "💡 For long or hot training sessions, electrolytes matter: try milk, fruit, or an electrolyte drink instead of water only.",
        "t4_btn": "🤖 Build my drinking schedule",
        "thinking": "The AI is thinking...",
        "no_key": "No AI key found. Add GROQ_API_KEY (and/or GEMINI_API_KEY) in Streamlit Secrets. See the README.",
        "error": "Connection problem. You may have hit the free limit, try again in a minute.",
        "details": "Error details",
    },
    "ar": {
        "page_title": "مدرب التغذية للطالب الرياضي",
        "hero_sub": "تغذية وترطيب وكشف خرافات للطالب اللي بيتمرن.",
        "sidebar_header": "🎛️ بياناتك",
        "weight": "الوزن (كجم)",
        "goal": "الهدف",
        "sport": "نوع الرياضة",
        "schedule": "موعد التمرين",
        "disclaimer": "⚠️ النتائج إرشادية وليست بديلاً عن أخصائي تغذية أو طبيب.",
        "goals": {"muscle": "💪 بناء عضلات", "fat": "🔥 حرق دهون", "focus": "⚡ طاقة وتركيز"},
        "sports": {"gym": "🏋️ جيم", "football": "⚽ كرة قدم", "running": "🏃 جري"},
        "schedules": {"before": "🌅 قبل المحاضرات", "after": "🌇 بعد المحاضرات", "between": "🕑 بين المحاضرات"},
        "tabs": ["🍽️ الماكروز والطبق", "🎒 Lunch Box والتمرين", "🕵️ كاشف الشائعات", "💧 الترطيب"],
        "t1_sub": "احتياجك اليومي التقريبي",
        "calories": "السعرات",
        "protein": "البروتين",
        "carbs": "الكربوهيدرات",
        "fat_m": "الدهون",
        "g": "جم",
        "split": "السعرات بتيجي منين",
        "t1_caption": "الأرقام تقديرية بناءً على الوزن والهدف ونوع الرياضة.",
        "t1_btn": "🤖 اقترح لي طبق يومي متوازن",
        "t2_sub": "أنت في أنهي حالة دلوقتي؟",
        "situations": {
            "pre1": "🚶 رايح الكلية وعندي تمرين كمان ساعة",
            "pre3": "⏳ عندي تمرين كمان 3 ساعات",
            "post": "😮‍💨 خلصت تمرين حالاً وحاسس بإرهاق",
            "lunchbox": "🎒 محتاج Lunch Box طول اليوم",
        },
        "avoid": "حاجة مبتاكلهاش أو عندك حساسية منها (اختياري)",
        "t2_btn": "🤖 اقترح وجبات",
        "t3_sub": "سمعت خرافة في الجيم؟ اسأل هنا",
        "ex1": "هل لازم آخد بروتين بودر وكرياتين عشان أعمل جسم حلو؟",
        "ex2": "هل التمرين على معدة فاضية الصبح بيحرق دهون أسرع؟",
        "chat_ph": "اسأل عن أي خرافة أو سؤال تغذية...",
        "chat_hint": "كل سؤال بيتجاوب عليه لوحده.",
        "clear": "🗑️ امسح المحادثة",
        "t4_sub": "حاسبة الترطيب",
        "hours": "ساعات التمرين النهاردة",
        "intake": "بتشرب كام لتر تقريباً في اليوم؟",
        "target": "المطلوب يومياً",
        "gap": "لسه محتاج تشرب",
        "progress": "تقدم شرب المية النهاردة",
        "liters": "لتر",
        "h_err": "🚨 شربك قليل جداً مقارنة بالمطلوب. الجفاف بيقلل التركيز والأداء.",
        "h_warn": "⚠️ محتاج تزود المية شوية.",
        "h_over": "⚠️ الإفراط الشديد في المية ممكن يخل بتوازن الأملاح. وزعيها على اليوم.",
        "h_ok": "✅ كمية كويسة.",
        "h_salts": "💡 مع التمرين الطويل أو الحر، الأملاح مهمة: جرب لبن، ثمار، أو مشروب أملاح بدل المية بس.",
        "t4_btn": "🤖 اعمللي جدول شرب",
        "thinking": "الذكاء الاصطناعي بيفكر...",
        "no_key": "مفيش مفتاح AI. ضيفي GROQ_API_KEY (و/أو GEMINI_API_KEY) في Streamlit Secrets. الخطوات في README.",
        "error": "حصلت مشكلة في الاتصال. ممكن توصلي للحد المجاني، جربي بعد دقيقة.",
        "details": "تفاصيل الخطأ",
    },
}

# English labels used inside AI prompts (the reply language is set by the system prompt)
GOAL_EN = {"muscle": "build muscle / bulk", "fat": "burn fat / cut", "focus": "energy and focus for lectures"}
SPORT_EN = {"gym": "gym / weightlifting", "football": "football", "running": "running and endurance"}
SCHEDULE_EN = {"before": "before classes", "after": "after classes", "between": "between classes"}
SITUATION_EN = {
    "pre1": "heading to campus with training in 1 hour",
    "pre3": "training in 3 hours",
    "post": "just finished training and feeling exhausted",
    "lunchbox": "needs a lunch box for a whole day on campus",
}

SYSTEM_BASE = """You are a sports nutrition coach for university students. Keep answers short and well organized.
- Rely only on established sports-nutrition science, and correct myths calmly.
- Suggest cheap, easy-to-find foods (chicken, eggs, tuna, fava beans, rice, brown bread, oats, bananas, milk, yogurt, nuts, peanut butter).
- Strictly forbidden: prescribing drugs, hormones, steroids or therapeutic doses, or diagnosing diseases. Refer the user to a doctor or dietitian in those cases.
- If the user is under 18, has a chronic illness, or is pregnant, advise seeing a doctor before any supplements or diets.
- If the question is unrelated to sports or nutrition, politely decline and steer back."""

SYSTEM_LANG = {
    "en": "Reply in simple, clear English.",
    "ar": "Reply in simple Egyptian colloquial Arabic (عامية مصرية مبسطة).",
}

# ───────────────────────── Styling ─────────────────────────
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
html, body, .stApp, .stMarkdown, p, h1, h2, h3, h4, label, button, input, textarea, li {
    font-family: 'Cairo', sans-serif !important;
}
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #14305a22, transparent), #0B1220; }
.block-container { padding-top: 2rem; max-width: 1100px; }

.hero {
    background: linear-gradient(120deg, #16A34A 0%, #0EA5A4 55%, #F97316 130%);
    border-radius: 24px; padding: 28px 32px; margin-bottom: 18px;
    box-shadow: 0 12px 40px rgba(34,197,94,.20);
}
.hero h1 { margin: 0; color: #fff; font-size: 2rem; font-weight: 800; }
.hero p { margin: 6px 0 0; color: #ECFDF5; font-size: 1.05rem; }

.mcard {
    border-radius: 20px; padding: 18px 12px; text-align: center; color: #fff;
    box-shadow: 0 8px 24px rgba(0,0,0,.25); transition: transform .2s ease;
}
.mcard:hover { transform: translateY(-4px); }
.micon { font-size: 1.6rem; }
.mval { font-size: 1.9rem; font-weight: 800; line-height: 1.2; }
.munit { font-size: .95rem; font-weight: 600; opacity: .9; }
.mlabel { font-size: .95rem; opacity: .95; font-weight: 600; }

.splitbar { display: flex; height: 16px; border-radius: 99px; overflow: hidden; margin: 8px 0 6px; }
.splitlegend { display: flex; gap: 16px; flex-wrap: wrap; font-size: .9rem; opacity: .9; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-inline-end: 6px; }

div.stButton > button {
    border-radius: 14px; border: 0; padding: .65rem 1.2rem; font-weight: 700;
    background: linear-gradient(135deg, #22C55E, #0EA5A4); color: #04140B;
    transition: transform .15s ease, box-shadow .15s ease;
}
div.stButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 8px 22px rgba(34,197,94,.35); color: #04140B;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 14px; padding: 10px 16px; background: rgba(255,255,255,.05); font-weight: 700;
}
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #22C55E55, #F9731655); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

[data-testid="stSidebar"] { background: #0F1830; border-inline-end: 1px solid rgba(255,255,255,.06); }
[data-testid="stChatMessage"] { border-radius: 18px; background: rgba(255,255,255,.04); }
</style>
"""

RTL_CSS = """
<style>
.stApp, [data-testid="stSidebar"] { direction: rtl; text-align: right; }
</style>
"""

# ───────────────────────── Language switch ─────────────────────────
with st.sidebar:
    lang_label = st.radio("Language / اللغة", ["English", "العربية"], horizontal=True)
lang = "ar" if lang_label == "العربية" else "en"
T = TEXT[lang]

st.markdown(BASE_CSS, unsafe_allow_html=True)
if lang == "ar":
    st.markdown(RTL_CSS, unsafe_allow_html=True)


# ───────────────────────── AI connection ─────────────────────────
def get_secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return default


def _ask_groq(prompt, api_key, models, lang):
    client = Groq(api_key=api_key)
    system = SYSTEM_BASE + "\n" + SYSTEM_LANG[lang]
    last_error = None
    for model in models:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=2000,
            )
            text = r.choices[0].message.content
            if text:
                return text
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Groq: {last_error}")


def _ask_gemini(prompt, api_key, models, lang):
    client = genai.Client(api_key=api_key)
    system = SYSTEM_BASE + "\n" + SYSTEM_LANG[lang]
    last_error = None
    for model in models:
        try:
            r = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=system, temperature=0.4),
            )
            if r.text:
                return r.text
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Gemini: {last_error}")


@st.cache_data(ttl=3600, show_spinner=False)
def ask_ai(prompt, lang, groq_key, gemini_key, groq_models, gemini_models):
    """Tries Groq first, then Gemini. Results are cached for an hour to save free quota."""
    errors = []
    if groq_key:
        try:
            return _ask_groq(prompt, groq_key, groq_models, lang)
        except Exception as e:
            errors.append(str(e))
    if gemini_key:
        try:
            return _ask_gemini(prompt, gemini_key, gemini_models, lang)
        except Exception as e:
            errors.append(str(e))
    raise RuntimeError(" | ".join(errors) or "no api keys")


def get_ai(prompt: str):
    """Returns (text, error_detail). error_detail is None on success."""
    groq_key = get_secret("GROQ_API_KEY")
    gemini_key = get_secret("GEMINI_API_KEY")
    if not groq_key and not gemini_key:
        return None, "NO_KEY"
    groq_models = (get_secret("GROQ_MODEL"),) if get_secret("GROQ_MODEL") else tuple(GROQ_MODELS)
    gemini_models = (get_secret("GEMINI_MODEL"),) if get_secret("GEMINI_MODEL") else tuple(GEMINI_MODELS)
    try:
        return ask_ai(prompt, lang, groq_key, gemini_key, groq_models, gemini_models), None
    except Exception as e:
        return None, str(e)


def show_error(detail):
    if detail == "NO_KEY":
        st.error(T["no_key"])
    else:
        st.error(T["error"])
        with st.expander(T["details"]):
            st.code(detail)


@st.dialog("🤖 AI Coach", width="large")
def ai_dialog(prompt):
    with st.spinner(T["thinking"]):
        text, err = get_ai(prompt)
    if text:
        st.markdown(text)
    else:
        show_error(err)


# ───────────────────────── Calculations (no AI) ─────────────────────────
def calc_macros(weight, goal, sport):
    kcal_per_kg = {"gym": 33, "football": 36, "running": 38}[sport]
    maintenance = weight * kcal_per_kg

    if goal == "muscle":
        calories, protein_per_kg, fat_per_kg = maintenance * 1.10, 2.0, 0.9
    elif goal == "fat":
        calories, protein_per_kg, fat_per_kg = maintenance * 0.80, 2.2, 0.8
    else:
        calories, protein_per_kg, fat_per_kg = maintenance, 1.6, 0.9

    protein = weight * protein_per_kg
    fat = weight * fat_per_kg
    carbs = max((calories - protein * 4 - fat * 9) / 4, 0)
    return round(calories), round(protein), round(carbs), round(fat)


def calc_water(weight, sport, hours):
    per_hour = {"gym": 600, "football": 750, "running": 800}[sport]
    return (weight * 35 + per_hour * hours) / 1000  # liters


def card(icon, label, value, unit, c1, c2):
    return (
        f'<div class="mcard" style="background:linear-gradient(135deg,{c1},{c2})">'
        f'<div class="micon">{icon}</div>'
        f'<div class="mval">{value}<span class="munit"> {unit}</span></div>'
        f'<div class="mlabel">{label}</div></div>'
    )


# ───────────────────────── Sidebar ─────────────────────────
with st.sidebar:
    st.header(T["sidebar_header"])
    weight = st.number_input(T["weight"], min_value=30.0, max_value=200.0, value=70.0, step=0.5)
    goal = st.pills(T["goal"], list(T["goals"].keys()), default="muscle",
                    format_func=lambda k: T["goals"][k]) or "muscle"
    sport = st.pills(T["sport"], list(T["sports"].keys()), default="gym",
                     format_func=lambda k: T["sports"][k]) or "gym"
    schedule = st.pills(T["schedule"], list(T["schedules"].keys()), default="after",
                        format_func=lambda k: T["schedules"][k]) or "after"
    st.divider()
    st.caption(T["disclaimer"])

# ───────────────────────── Hero ─────────────────────────
st.markdown(
    f'<div class="hero"><h1>💪 {T["page_title"]}</h1><p>{T["hero_sub"]}</p></div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(T["tabs"])

# ───────────────────────── Tab 1 ─────────────────────────
with tab1:
    calories, protein, carbs, fat = calc_macros(weight, goal, sport)
    st.subheader(T["t1_sub"])
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(card("🔥", T["calories"], calories, "kcal", "#F97316", "#EA580C"), unsafe_allow_html=True)
    c2.markdown(card("🥩", T["protein"], protein, T["g"], "#16A34A", "#15803D"), unsafe_allow_html=True)
    c3.markdown(card("🍚", T["carbs"], carbs, T["g"], "#0EA5E9", "#0369A1"), unsafe_allow_html=True)
    c4.markdown(card("🥜", T["fat_m"], fat, T["g"], "#EAB308", "#A16207"), unsafe_allow_html=True)

    kp, kc, kf = protein * 4, carbs * 4, fat * 9
    total = max(kp + kc + kf, 1)
    pp, pc, pf = round(kp / total * 100), round(kc / total * 100), round(kf / total * 100)
    st.markdown(f"**{T['split']}**")
    st.markdown(
        f'<div class="splitbar">'
        f'<div style="width:{pp}%;background:#16A34A"></div>'
        f'<div style="width:{pc}%;background:#0EA5E9"></div>'
        f'<div style="width:{pf}%;background:#EAB308"></div></div>'
        f'<div class="splitlegend">'
        f'<span><span class="dot" style="background:#16A34A"></span>{T["protein"]} {pp}%</span>'
        f'<span><span class="dot" style="background:#0EA5E9"></span>{T["carbs"]} {pc}%</span>'
        f'<span><span class="dot" style="background:#EAB308"></span>{T["fat_m"]} {pf}%</span></div>',
        unsafe_allow_html=True,
    )
    st.caption(T["t1_caption"])

    if st.button(T["t1_btn"], key="plate"):
        ai_dialog(
            f"A university student weighing {weight} kg. Goal: {GOAL_EN[goal]}. Sport: {SPORT_EN[sport]}. "
            f"Training time: {SCHEDULE_EN[schedule]}.\n"
            f"Daily needs: {calories} kcal, protein {protein} g, carbs {carbs} g, fat {fat} g.\n"
            "Suggest 4 meals across the day with amounts in grams (protein, carbs, healthy fats) using cheap, "
            "common foods, in a short table, then give just two tips."
        )

# ───────────────────────── Tab 2 ─────────────────────────
with tab2:
    st.subheader(T["t2_sub"])
    situation = st.pills("situation", list(T["situations"].keys()), default="pre1",
                         format_func=lambda k: T["situations"][k], label_visibility="collapsed") or "pre1"
    avoid = st.text_input(T["avoid"], max_chars=100)

    if st.button(T["t2_btn"], key="meals"):
        ai_dialog(
            f"A student weighing {weight} kg. Goal: {GOAL_EN[goal]}. Sport: {SPORT_EN[sport]}. "
            f"Situation: {SITUATION_EN[situation]}.\n"
            f"Foods to avoid: {avoid or 'none'}.\n"
            "Suggest 3 quick, practical options that can be eaten on campus, with amounts and the best timing, "
            "and a short reason for each."
        )

# ───────────────────────── Tab 3 (chat) ─────────────────────────
with tab3:
    st.subheader(T["t3_sub"])
    if "chat" not in st.session_state:
        st.session_state.chat = []

    e1, e2, e3 = st.columns([1, 1, 0.5])
    pending = None
    if e1.button(T["ex1"], key="ex1"):
        pending = T["ex1"]
    if e2.button(T["ex2"], key="ex2"):
        pending = T["ex2"]
    if e3.button(T["clear"], key="clear"):
        st.session_state.chat = []
        st.rerun()

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input(T["chat_ph"], max_chars=500) or pending
    if q:
        st.session_state.chat.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner(T["thinking"]):
                text, err = get_ai(
                    f"Question from an athlete student (weight {weight} kg, goal: {GOAL_EN[goal]}):\n"
                    f"\"{q.strip()}\"\n"
                    "Answer in this format: 1) Verdict (fact / myth / partly true) "
                    "2) Simple scientific explanation 3) Practical advice."
                )
            if text:
                st.markdown(text)
                st.session_state.chat.append({"role": "assistant", "content": text})
            else:
                show_error(err)
    st.caption(T["chat_hint"])

# ───────────────────────── Tab 4 ─────────────────────────
with tab4:
    st.subheader(T["t4_sub"])
    s1, s2 = st.columns(2)
    hours = s1.slider(T["hours"], 0.0, 6.0, 1.0, 0.5)
    intake = s2.slider(T["intake"], 0.0, 8.0, 1.5, 0.25)

    target = calc_water(weight, sport, hours)
    remaining = max(target - intake, 0)
    k1, k2 = st.columns(2)
    k1.markdown(card("🎯", T["target"], f"{target:.1f}", T["liters"], "#0EA5E9", "#0369A1"), unsafe_allow_html=True)
    k2.markdown(card("🥤", T["gap"], f"{remaining:.1f}", T["liters"], "#14B8A6", "#0F766E"), unsafe_allow_html=True)

    st.write("")
    st.markdown(f"**{T['progress']}**")
    st.progress(min(intake / target, 1.0) if target else 0.0)

    if intake < target * 0.6:
        st.error(T["h_err"])
    elif intake < target * 0.85:
        st.warning(T["h_warn"])
    elif intake > 5:
        st.warning(T["h_over"])
    else:
        st.success(T["h_ok"])

    if hours >= 1.5 or sport == "football":
        st.info(T["h_salts"])

    if st.button(T["t4_btn"], key="water"):
        ai_dialog(
            f"A student weighing {weight} kg, sport: {SPORT_EN[sport]}, training {SCHEDULE_EN[schedule]} "
            f"for {hours} hours. Currently drinks {intake} L per day; target is about {target:.1f} L.\n"
            "Build a water drinking schedule across the study day and training (before/during/after), "
            "warn about common hydration mistakes, and keep it brief."
        )