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
        "page_title": "💪 Student Athlete Nutrition Coach",
        "sidebar_header": "🎛️ Your details",
        "weight": "Weight (kg)",
        "goal": "Goal",
        "sport": "Sport",
        "schedule": "Training time relative to classes",
        "disclaimer": "⚠️ Results are general guidance, not a substitute for a dietitian or doctor.",
        "goals": {"muscle": "Build muscle / bulk", "fat": "Burn fat / cut", "focus": "Energy & focus for lectures"},
        "sports": {"gym": "Gym / weightlifting", "football": "Football", "running": "Running & endurance"},
        "schedules": {"before": "Before classes", "after": "After classes", "between": "Between classes"},
        "tabs": ["🍽️ Macros & Plate", "🎒 Lunch Box & Pre/Post Workout", "🕵️ Myth Buster", "💧 Hydration"],
        "t1_sub": "Your approximate daily needs",
        "calories": "Calories",
        "protein": "Protein",
        "carbs": "Carbs",
        "fat_m": "Fat",
        "g": "g",
        "t1_caption": "Estimates based on your weight, goal and sport.",
        "t1_btn": "🤖 Suggest a balanced daily plate",
        "t2_sub": "Which situation are you in right now?",
        "t2_select": "Choose your situation",
        "situations": {
            "pre1": "Heading to campus, training in 1 hour",
            "pre3": "Training in 3 hours",
            "post": "Just finished training and feeling exhausted",
            "lunchbox": "Need a lunch box for the whole day on campus",
        },
        "avoid": "Foods you avoid or are allergic to (optional)",
        "t2_btn": "🤖 Suggest meals",
        "t3_sub": "Heard a gym myth? Ask here",
        "t3_caption": "Example: Do I need protein powder and creatine to build a good physique? / Does fasted morning training burn fat faster?",
        "t3_input": "Type your question",
        "t3_btn": "🔍 Reveal the truth",
        "t3_short": "Please write a clearer question.",
        "t4_sub": "Hydration calculator",
        "hours": "Training hours today",
        "intake": "How many liters do you drink per day (roughly)?",
        "target": "Daily target",
        "gap": "Difference from what you drink",
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
        "page_title": "💪 مدرب التغذية للطالب الرياضي",
        "sidebar_header": "🎛️ بياناتك",
        "weight": "الوزن (كجم)",
        "goal": "الهدف",
        "sport": "نوع الرياضة",
        "schedule": "موعد التمرين بالنسبة للجامعة",
        "disclaimer": "⚠️ النتائج إرشادية وليست بديلاً عن أخصائي تغذية أو طبيب.",
        "goals": {"muscle": "بناء عضلات / تضخيم", "fat": "حرق دهون / تنشيف", "focus": "طاقة وتركيز للمحاضرات"},
        "sports": {"gym": "جيم / رفع أثقال", "football": "كرة قدم", "running": "جري وتحمل"},
        "schedules": {"before": "قبل المحاضرات", "after": "بعد المحاضرات", "between": "بين المحاضرات"},
        "tabs": ["🍽️ الماكروز والطبق", "🎒 Lunch Box وقبل/بعد التمرين", "🕵️ كاشف الشائعات", "💧 الترطيب"],
        "t1_sub": "احتياجك اليومي التقريبي",
        "calories": "السعرات",
        "protein": "البروتين",
        "carbs": "الكربوهيدرات",
        "fat_m": "الدهون",
        "g": "جم",
        "t1_caption": "الأرقام تقديرية بناءً على الوزن والهدف ونوع الرياضة.",
        "t1_btn": "🤖 اقترح لي طبق يومي متوازن",
        "t2_sub": "أنت في أنهي حالة دلوقتي؟",
        "t2_select": "اختار حالتك",
        "situations": {
            "pre1": "رايح الكلية وعندي تمرين كمان ساعة",
            "pre3": "عندي تمرين كمان 3 ساعات",
            "post": "خلصت تمرين حالاً وحاسس بإرهاق",
            "lunchbox": "محتاج Lunch Box للجامعة طول اليوم",
        },
        "avoid": "حاجة مبتاكلهاش أو عندك حساسية منها (اختياري)",
        "t2_btn": "🤖 اقترح وجبات",
        "t3_sub": "سمعت خرافة في الجيم؟ اسأل هنا",
        "t3_caption": "مثال: هل لازم آخد بروتين بودر وكرياتين عشان أعمل جسم حلو؟ / هل التمرين على معدة فاضية بيحرق دهون أسرع؟",
        "t3_input": "اكتب سؤالك",
        "t3_btn": "🔍 كشف الحقيقة",
        "t3_short": "اكتبي سؤال أوضح شوية.",
        "t4_sub": "حاسبة الترطيب",
        "hours": "ساعات التمرين النهاردة",
        "intake": "بتشرب كام لتر تقريباً في اليوم؟",
        "target": "المطلوب يومياً",
        "gap": "الفرق عن اللي بتشربه",
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


# ───────────────────────── Language switch ─────────────────────────
with st.sidebar:
    lang_label = st.radio("Language / اللغة", ["English", "العربية"], horizontal=True)
lang = "ar" if lang_label == "العربية" else "en"
T = TEXT[lang]

if lang == "ar":
    st.markdown(
        """
        <style>
        .stApp, [data-testid="stSidebar"] { direction: rtl; text-align: right; }
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { direction: rtl; }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def run_ai(prompt: str):
    groq_key = get_secret("GROQ_API_KEY")
    gemini_key = get_secret("GEMINI_API_KEY")
    if not groq_key and not gemini_key:
        st.error(T["no_key"])
        return
    groq_models = (get_secret("GROQ_MODEL"),) if get_secret("GROQ_MODEL") else tuple(GROQ_MODELS)
    gemini_models = (get_secret("GEMINI_MODEL"),) if get_secret("GEMINI_MODEL") else tuple(GEMINI_MODELS)
    with st.spinner(T["thinking"]):
        try:
            st.markdown(ask_ai(prompt, lang, groq_key, gemini_key, groq_models, gemini_models))
        except Exception as e:
            st.error(T["error"])
            with st.expander(T["details"]):
                st.code(str(e))


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


# ───────────────────────── Sidebar ─────────────────────────
with st.sidebar:
    st.header(T["sidebar_header"])
    weight = st.number_input(T["weight"], min_value=30.0, max_value=200.0, value=70.0, step=0.5)
    goal = st.selectbox(T["goal"], list(T["goals"].keys()), format_func=lambda k: T["goals"][k])
    sport = st.selectbox(T["sport"], list(T["sports"].keys()), format_func=lambda k: T["sports"][k])
    schedule = st.selectbox(T["schedule"], list(T["schedules"].keys()), format_func=lambda k: T["schedules"][k])
    st.divider()
    st.caption(T["disclaimer"])

st.title(T["page_title"])

tab1, tab2, tab3, tab4 = st.tabs(T["tabs"])

# ───────────────────────── Tab 1 ─────────────────────────
with tab1:
    calories, protein, carbs, fat = calc_macros(weight, goal, sport)
    st.subheader(T["t1_sub"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["calories"], f"{calories} kcal")
    c2.metric(T["protein"], f"{protein} {T['g']}")
    c3.metric(T["carbs"], f"{carbs} {T['g']}")
    c4.metric(T["fat_m"], f"{fat} {T['g']}")
    st.caption(T["t1_caption"])

    if st.button(T["t1_btn"], key="plate"):
        run_ai(
            f"A university student weighing {weight} kg. Goal: {GOAL_EN[goal]}. Sport: {SPORT_EN[sport]}. "
            f"Training time: {SCHEDULE_EN[schedule]}.\n"
            f"Daily needs: {calories} kcal, protein {protein} g, carbs {carbs} g, fat {fat} g.\n"
            "Suggest 4 meals across the day with amounts in grams (protein, carbs, healthy fats) using cheap, "
            "common foods, in a short table, then give just two tips."
        )

# ───────────────────────── Tab 2 ─────────────────────────
with tab2:
    st.subheader(T["t2_sub"])
    situation = st.selectbox(T["t2_select"], list(T["situations"].keys()), format_func=lambda k: T["situations"][k])
    avoid = st.text_input(T["avoid"], max_chars=100)

    if st.button(T["t2_btn"], key="meals"):
        run_ai(
            f"A student weighing {weight} kg. Goal: {GOAL_EN[goal]}. Sport: {SPORT_EN[sport]}. "
            f"Situation: {SITUATION_EN[situation]}.\n"
            f"Foods to avoid: {avoid or 'none'}.\n"
            "Suggest 3 quick, practical options that can be eaten on campus, with amounts and the best timing, "
            "and a short reason for each."
        )

# ───────────────────────── Tab 3 ─────────────────────────
with tab3:
    st.subheader(T["t3_sub"])
    st.caption(T["t3_caption"])
    question = st.text_area(T["t3_input"], max_chars=500, height=100)

    if st.button(T["t3_btn"], key="myth"):
        if len(question.strip()) < 5:
            st.warning(T["t3_short"])
        else:
            run_ai(
                f"Question from an athlete student (weight {weight} kg, goal: {GOAL_EN[goal]}):\n"
                f"\"{question.strip()}\"\n"
                "Answer in this format: 1) Verdict (fact / myth / partly true) 2) Simple scientific explanation "
                "3) Practical advice."
            )

# ───────────────────────── Tab 4 ─────────────────────────
with tab4:
    st.subheader(T["t4_sub"])
    hours = st.number_input(T["hours"], min_value=0.0, max_value=6.0, value=1.0, step=0.5)
    intake = st.number_input(T["intake"], min_value=0.0, max_value=8.0, value=1.5, step=0.25)

    target = calc_water(weight, sport, hours)
    gap = target - intake
    c1, c2 = st.columns(2)
    c1.metric(T["target"], f"{target:.1f} {T['liters']}")
    c2.metric(T["gap"], f"{gap:+.1f} {T['liters']}")

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
        run_ai(
            f"A student weighing {weight} kg, sport: {SPORT_EN[sport]}, training {SCHEDULE_EN[schedule]} "
            f"for {hours} hours. Currently drinks {intake} L per day; target is about {target:.1f} L.\n"
            "Build a water drinking schedule across the study day and training (before/during/after), "
            "warn about common hydration mistakes, and keep it brief."
        )
