import asyncio
from app.container import container
from langchain_core.messages import SystemMessage, HumanMessage

qwen35 = container.qwen_35()

a_doctor = {
    "id": 47,
    "name": "دکتر سارا رحیمی",
    "profession": "متخصص دندانپزشکی ترمیمی و زیبایی",
    "title": "رییس بخش دندانپزشکی ترمیمی",
    "description": "متخصص برجسته دندانپزشکی ترمیمی و زیبایی با تمرکز بر درمان‌های بدون درد، لمینت سرامیکی، ایمپلنت‌های دیجیتال و ارتودنسی نامرئی. همکار رسمی کلینیک‌های بین‌المللی و عضو انجمن دندانپزشکی زیبایی اروپا.",
    "specialties": ["ایمپلنت دیجیتال", "لمینت سرامیکی", "ارتودنسی نامرئی (اینویزیلاین)", "درمان ریشه (اندو)", "جراحی لثه", "بلیچینگ پیشرفته"],
    "experience_years": 14,
    "education": "فلوشیپ ایمپلنتولوژی - دانشگاه برن سوئیس",
    "hospital": "کلینیک تخصصی دندانپزشکی مدرن",
    "location": "تهران، خیابان ولیعصر، بالاتر از میدان ونک، پلاک ۱۲۳",
    "rating": 489,
    "reviews_count": 234,
    "availability": ["شنبه", "یکشنبه", "سه‌شنبه", "پنجشنبه"],
    "consultation_fee": 280,
    "phone": "۰۲۱-۸۸۷۷-۱۲۳۴",
    "email": "dr.sara.rahimi@moderndental.com",
    "is_accepting_patients": True,
    "languages": ["فارسی", "انگلیسی", "آلمانی (مقدماتی)"],
    "profile_image": "sara_rahimi.jpg"
}

async def ask_date(state):
    context = ""
    candidate_doctor = state["chosen_doctor"]
    
    context += "doctor's name: " + candidate_doctor['name'] + "\nprofession: " +  candidate_doctor['profession'] + \
    "\navailablity day: " + ", ".join(candidate_doctor['availability'])

    content=f"""You a receptionist in a clinic.
Do not greet the user, and make the questions concise.
Ask human about his/her prefered date for appointment.
Primary language is Persian, unless user speaks another.
{context}"""

    res = await qwen35.ainvoke(content)
    
    return {"messages": [res]}


if __name__ == "__main__":
    asyncio.run(ask_date({"chosen_doctor": a_doctor}))