from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import jdatetime
from enum import Enum
from pydantic import BaseModel, Field


class AppointmentTime(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)

import re

def extract_time(text):
    # Match Persian digits (۰-۹), English digits (0-9), and colon
    match = re.search(r'[۰-۹0-9:]+', text)
    return match.group(0) if match else ""


pay_load = {
        "id": 2,
        "name": "دکتر مایکل چن",
        "profession": "متخصص مغز و اعصاب",
        "title": "رئیس بخش مغز و اعصاب",
        "description": "متخصص در اختلالات نورودژنراتیو و توانبخشی سکته مغزی. تحقیقات پیشگام در زمینه بیماری آلزایمر و درمان پارکینسون.",
        "specialties": ["اختلالات نورودژنراتیو", "توانبخشی سکته مغزی", "اختلالات حرکتی"],
        "experience_years": 20,
        "education": "دکترای تخصصی و فوق دکترای علوم اعصاب - دانشگاه جانز هاپکینز",
        "hospital": "مرکز علوم اعصاب پاسیفیک",
        "location": "مشهد، بلوار وکیل‌آباد",
        "rating": 408,
        "reviews_count": 287,
        "availability": ["یکشنبه", "سه‌شنبه", "پنجشنبه"],
        "consultation_fee": 300,
        "phone": "۰۵۱-۵۵۵۵-۰۴۵۶",
        "email": "dr.michael.chen@pacificneuro.com",
        "is_accepting_patients": True,
        "languages": ["فارسی", "انگلیسی", "ماندارین"],
        "profile_image": "michael_chen.jpg"
    }


class Weekday(str, Enum):
    SATURDAY = "saturday"
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"


PERSIAN_TO_WEEKDAY = {
    "شنبه": 5,
    "یکشنبه": 6,
    "دوشنبه": 0,
    "سه‌شنبه": 1,
    "چهارشنبه": 2,
    "پنجشنبه": 3,
    "جمعه": 4,
}

PYTHON_WEEKDAYS = {
    Weekday.MONDAY: 0,
    Weekday.TUESDAY: 1,
    Weekday.WEDNESDAY: 2,
    Weekday.THURSDAY: 3,
    Weekday.FRIDAY: 4,
    Weekday.SATURDAY: 5,
    Weekday.SUNDAY: 6,
}
PYTHON_WEEKDAYS = {
    0: Weekday.MONDAY
}

PERSIAN_WEEKDAYS = {
    0: "دوشنبه",
    1: "سه‌شنبه",
    2: "چهارشنبه",
    3: "پنجشنبه",
    4: "جمعه",
    5: "شنبه",
    6: "یکشنبه",
}

def find_next_available_appointment(
    doctor,
    chosen_day: str,
    chosen_time: AppointmentTime | None = None,
):
    """Find the next available appointment on the chosen weekday."""

    if not doctor["is_accepting_patients"]:
        return None

    print(doctor['availability'])
    print(PERSIAN_TO_WEEKDAY[chosen_day])
    # Doctor doesn't work on the requested day.
    doctor_availability_day_index = [PERSIAN_TO_WEEKDAY[x] for x in doctor['availability']]
    print(doctor_availability_day_index)
    if PERSIAN_TO_WEEKDAY[chosen_day] not in doctor_availability_day_index:
        return None

    now = datetime.now(ZoneInfo("Asia/Tehran"))

    # Get Python's weekday number for the selected day.
    

    days_ahead = (PERSIAN_TO_WEEKDAY[chosen_day] - now.weekday()) % 7

    candidate = now + timedelta(days=days_ahead)

    # Default: 10:00 if no time was specified.
    time = "۱۰:۰۰"
    
    print("HELLOOOO")
    print(time)

    if chosen_time is not None:
        time = chosen_time
    time = extract_time(time)
    
    appointment_time = candidate.replace(
        hour = int(time[:1]) if len(time) == 4 else int(time[:2]),
        minute=int(time[-2:]),
        second=0,
        microsecond=0,
    )

    print(appointment_time.hour, appointment_time.minute)

    # If the requested time has already passed, move to next week.
    if appointment_time <= now:
        appointment_time += timedelta(days=7)

    return appointment_time


def format_appointment_confirmation(doctor, appointment_time, patient_name):
    """Create a formal patient-facing appointment confirmation."""

    if appointment_time is None:
        return "برای زمان انتخاب‌شده، نوبت قابل رزرو یافت نشد."

    jalali = jdatetime.datetime.fromgregorian(
        datetime=appointment_time
    )

    weekday = PERSIAN_WEEKDAYS[appointment_time.weekday()]

    return f"""
تأیید نوبت ویزیت

نوبت شما با موفقیت ثبت شد.

اطلاعات پزشک
نام پزشک: {doctor["name"]}
تخصص: {doctor["profession"]}

اطلاعات نوبت
تاریخ: {weekday} {jalali.day} {jalali.strftime("%B")} {jalali.year}
ساعت: {appointment_time.strftime("%H:%M")}

محل مراجعه
{doctor["hospital"]}
{doctor["location"]}

اطلاعات بیمار
نام بیمار: {patient_name}

هزینه ویزیت
{doctor["consultation_fee"]:,} تومان

شماره تماس مرکز
{doctor["phone"]}

کد پیگیری
AP-{doctor["id"]}-{jalali.strftime("%y%m%d%H%M")}

وضعیت نوبت: تأیید شده

لطفاً ۱۰ تا ۱۵ دقیقه پیش از زمان تعیین‌شده در مرکز حضور داشته باشید.
"""





if __name__ == "__main__":
    # --------------------------------------------------
    # Example
    # --------------------------------------------------

    patient_name = "محمد علی"

    appointment = find_next_available_appointment(
        doctor=pay_load,
        chosen_day="یکشنبه",
        chosen_time="ساعت ۱۰",
    )
    if appointment is None:
        print("هیچ نوبت نزدیکی برای این پزشک پیدا نشد.")
    else:
        confirmation = format_appointment_confirmation(
            doctor=pay_load,
            appointment_time=appointment,
            patient_name=patient_name,
        )

        print(confirmation)