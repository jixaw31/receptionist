from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import SystemMessage
from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional, Literal

class UserIntent(BaseModel):
    """Classification of user intent in medical assistant context"""
    category: Literal["casual", 
    "look_for_doctor", "doctor_exists"] = Field(
        ...,
        description="Primary category of user intent"
    )
    doctor_name: Optional[str] = Field(
        None,
        description="Extracted doctor's full name if mentioned. If user approved him."
    )
    intent: Optional[Literal["book_appointment", "query_info", "other"]] = Field(
        None,
        description="Specific user action when doctor_exists. Only populate when category is 'doctor_exists'."
    )

SYSTEM_PROMPT = """Classify the user's intent into one of three categories. For certain categories, extract additional information.

**Categories:**

1. **casual**: 
   - Greetings, thanks, farewells, or general conversation not related to finding or booking a doctor.
   - Examples: "Hello", "Thanks", "How are you?", "Goodbye", "That's helpful".

2. **look_for_doctor**: 
   - User is searching for a doctor but does NOT mention a specific doctor's name.
   - They may mention:
     - Specialty: "I need a cardiologist", "Looking for a dermatologist"
     - Location: "Find a doctor in Tehran", "Any neurologist near me"
     - General inquiry: "I want to book an appointment with any doctor", "Need to see a specialist"
     - Condition-based: "I have back pain, need a doctor"
   - **Key indicator**: No specific name is mentioned (no "Dr.", "Doctor", or full name).
   - If the user mentions a condition but no doctor name → still **look_for_doctor**.
   - If the user is vague ("I need an appointment") → still **look_for_doctor**.

3. **doctor_exists**:

   * User explicitly mentions a specific doctor's name (title + name, first name, last name, or full name).
   * AI proposes a doctor to user and user accepts.
   * Includes cases where they also mention booking, appointment, availability, or asking questions.
   * Examples:

     * "I want to book with Dr. Jones" → doctor_exists
     * "When is Dr. Smith available?" → doctor_exists
     * "I need to see Dr. Alavi" → doctor_exists
     * "Is Dr. Chen accepting patients?" → doctor_exists
   * **Key indicator**: ANY doctor name is mentioned, regardless of the action.
   * If the AI previously proposed one or more doctors and the user's response selects or accepts a proposed doctor, set `doctor_name` to the corresponding proposed doctor's name, even if the user does not repeat the name.
   * If the AI proposed a single doctor and the user accepts, set `doctor_name` to that doctor's name. If multiple doctors were proposed, resolve the user's selection to the corresponding doctor's name.

Extract TWO additional fields:

* **doctor_name**: Extract the exact doctor name as mentioned (include title if present).

  * If the AI previously proposed a doctor and the user accepts or selects that doctor, extract the proposed doctor's name exactly as it appeared in the AI's message.
  * Examples: "Dr. Jones", "Dr. Smith", "Dr. Alavi", "Dr. Chen"
  * If the user says "Dr. Sarah Johnson" → extract "Dr. Sarah Johnson"
  * If the user says "Dr. Jones" → extract "Dr. Jones"
  * If the user says "Sarah Johnson" → extract "Sarah Johnson"


- **action**: Determine the user's specific action:
  - "book_appointment": User wants to schedule, book, or make an appointment
    - Keywords: "book", "schedule", "make appointment", "set up", "get an appointment", "وقت ملاقات", "نوبت"
  - "query_info": User asks about availability, policies, or general information
    - Keywords: "available", "when", "accepting patients", "specialty", "clinic", "where", "آیا", "کی", "کجا"
    - Questions about the doctor's practice, schedule, or policies
  - "other": Any other action (e.g., general mention, complaint, recommendation)

**Decision Rules:**
1. FIRST check if a doctor's name is mentioned → if YES, category = "doctor_exists"
2. If NO doctor name → check if searching for a doctor → category = "look_for_doctor"
3. If neither → category = "casual"
4. When category = "doctor_exists", ALWAYS populate doctor_name and action
5. When category is NOT "doctor_exists", leave doctor_name and action as null

**Examples:**

Input: "Hello" → category: "casual", doctor_name: null, action: null

Input: "I need a cardiologist" → category: "look_for_doctor", doctor_name: null, action: null

Input: "Find a dermatologist in Tehran" → category: "look_for_doctor", doctor_name: null, action: null

Input: "I have back pain, need to see someone" → category: "look_for_doctor", doctor_name: null, action: null

Input: "I want to book with Dr. Jones" → category: "doctor_exists", doctor_name: "Dr. Jones", action: "book_appointment"

Input: "When is Dr. Smith available?" → category: "doctor_exists", doctor_name: "Dr. Smith", action: "query_info"

Input: "Is Dr. Alavi accepting new patients?" → category: "doctor_exists", doctor_name: "Dr. Alavi", action: "query_info"

Input: "من یه وقت ملاقات با دکتر چن می خواستم" → category: "doctor_exists", doctor_name: "دکتر چن", action: "book_appointment"

Input: "آیا دکتر چن بیمار قبول می کنه؟" → category: "doctor_exists", doctor_name: "دکتر چن", action: "query_info"

Input: "دکتر احمدی کجا مطب داره؟" → category: "doctor_exists", doctor_name: "دکتر احمدی", action: "query_info"

Input: "I need an appointment" → category: "look_for_doctor", doctor_name: null, action: null

**CRITICAL:** 
- doctor_name must be EXACTLY as mentioned in the user's input
- For look_for_doctor, do NOT extract any name even if a specialty is mentioned
- The presence of ANY doctor name overrides everything else → category becomes "doctor_exists" """
   
# Priority: doctor_exists/look_for_doctor > greeting
# --- System Message Object ---
system_message = SystemMessage(content=SYSTEM_PROMPT)


gather_info_system_message = SystemMessage(
    content=f"""Extract patient information from the conversation.

Extract the following fields independently:

- patient_name: The patient's full name.
- city: The patient's city of residence.
- phone_number: The patient's phone number.
- Day: The patient's desired day of the week.‌ User may have typo like: سشنبه which should be categorized as سه شنبه
- Time: The patient's desired time of the day. Example: ۱۰ -> ۱۰:۰۰, ۵ عصر -> ۱۷:۰۰, Only take number as value for time.
For example if user said: صبح -> ۱۰:۰۰ , بعد از ظهر -> ۱۶:۰۰
Rules:
- A valid patient full name should be a must be proper personal name.
- Extract the patient name as: FirstName LastName
- Either field may be present without the other.
- All fields may be present.
- Neither field may be present.
- Only extract information explicitly stated in the conversation.
- Never guess, infer, or fabricate information.
- If a field is not explicitly provided, return None for that field.
"""
    )


from enum import Enum
from pydantic import BaseModel, Field


class Weekday(str, Enum):
    SATURDAY = "saturday"
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"


class AppointmentTime(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)


class UserInfo(BaseModel):
    city: str | None = Field(
        default=None,
        description=(
            "The city of residence of the patient. "
            "Return None if not provided."
        )
    )

    name: str | None = Field(
        default=None,
        description=(
            "The full name of the patient. "
            "Return None if not provided. "
            "The user may be making an appointment for someone else."
        )
    )

    phone_number: str | None = Field(
        default=None,
        description="The patient's phone number. Return None if not provided."
    )

    day: Literal["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"] | None = Field(
        default=None,
        description=(
            "The patient's desired day of the week."
            
        )
    )

    time: str | None = Field(
        default=None,
        description=(
            "The patient's desired appointment time, is a number always."
        )
    )