from app.container import container
from pydantic import BaseModel, Field
from typing import Optional, Literal
from langchain_core.messages import SystemMessage, HumanMessage

class DoctorInfo(BaseModel):
    name: Optional[str] = Field(
        None,
        description="The full name of the doctor mentioned in the user's input."
    )
    intent: Literal["book_appointment", "query_info", "other"] = Field(
        ...,
        description="The user's primary intent regarding the doctor"
    )



qwen35 = container.qwen_35()

qwen35_with_structured_output = qwen35.with_structured_output(DoctorInfo)

async def post_doctor_exists(state):

    print("NODE: post_doctor_exists")
    system_message = SystemMessage(content="""Extract TWO pieces of information from the user's input:

1. **Doctor's Name**: Identify and extract any doctor's name mentioned. Look for titles like "Dr.", "Doctor", "دکتر", or full names. If multiple names exist, extract the most relevant one. Return null if no doctor name is found.

2. **Intent**: Classify the user's intent as one of:
   - "book_appointment": User wants to schedule, book, or make an appointment
   - "query_info": User asks about availability, policies, or general information
   - "other": Any other intent

IMPORTANT: Always extract the name regardless of the intent. These are two separate tasks. Even if the user is asking a question, still extract the doctor's name.

Examples:
- "من یه وقت ملاقات با دکتر چن می خواستم." → name: "دکتر چن", intent: "book_appointment"
- "آیا دکتر چن بیمار قبول می کنه؟" → name: "دکتر چن", intent: "query_info"
- "دکتر احمدی کجا مطب داره؟" → name: "دکتر احمدی", intent: "query_info"
- "سلام، چطورید؟" → name: null, intent: "other"
- "میخوام با دکتر رضایی وقت بگیرم" → name: "دکتر رضایی", intent: "book_appointment"

Extract the name FIRST, then determine the intent. Both fields must be populated.""")

    res = await qwen35_with_structured_output.ainvoke([system_message]+ state['messages'])
    print(res)

    import sys;sys.exit()
    return {"doctor_mention_by_user": {"doctor_name": res.name, "user_intent": res.intent}}

