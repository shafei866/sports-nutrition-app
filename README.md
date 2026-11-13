# Student Athlete Nutrition Coach 💪 | مدرب التغذية للطالب الرياضي

Bilingual (English / العربية) Streamlit app powered by Groq (primary) and Gemini (fallback).
تطبيق Streamlit بالإنجليزي والعربي، متصل بـ Groq (أساسي) و Gemini (احتياطي).

## Run locally | التشغيل محلياً
1. `pip install -r requirements.txt`
2. Create `.streamlit/secrets.toml` | اعملي ملف `.streamlit/secrets.toml`:
```
GROQ_API_KEY = "your_key"
GEMINI_API_KEY = "your_key"
```
3. `python -m streamlit run app.py`

## Deploy free | النشر المجاني
1. Push to GitHub (never push secrets.toml) | ارفعي على GitHub (من غير secrets.toml)
2. share.streamlit.io → Create app → choose repo and `app.py`
3. Advanced settings → Secrets → paste the keys above | الصقي المفاتيح
4. Deploy

Free keys | المفاتيح المجانية: console.groq.com/keys · aistudio.google.com/apikey

⚠️ Guidance only, not a substitute for a dietitian or doctor. | النتائج إرشادية وليست بديلاً عن أخصائي تغذية أو طبيب.
