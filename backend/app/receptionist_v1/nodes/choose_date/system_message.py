from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field


class ChosenDate(BaseModel):
    day: str = Field(
        description="The day of the week exactly as written by the user in Persian."
    )
    hour: str | None = Field(
        default=None,
        description="The hour/time mentioned by the user, if any. Otherwise null."
    )

system_message = SystemMessage(content="""
Extract the user's chosen day of the week and, if provided, the time of day.

Rules:
1. Extract the day exactly as written by the user.
2. Do NOT correct spelling or normalize the day.
3. If the user does not mention an hour/time, return hour as null.
4. Extract the time exactly as written by the user.
5. Do NOT infer a time that the user did not explicitly provide.

Examples:

User: "روز مد نظر من سشنبه است."
Output:
day="سشنبه"
hour=null

User: "سه شنبه ساعت 10 میخوام."
Output:
day="سه شنبه"
hour="10"

User: "دوشنبه ساعت 10 صبح"
Output:
day="دوشنبه"
hour="10 صبح"

User: "پنجشنبه ساعت 14:30"
Output:
day="پنجشنبه"
hour="14:30"
""")

# the example
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