import asyncio
from langchain_core.messages import SystemMessage
from app.container import container
from typing import Literal
from pydantic import BaseModel, Field


class BookingDecision(BaseModel):
    decision: Literal[
        "select_doctor",
        "modify_criteria",
        "cancel_booking",
    ] = Field(
        description="The user's decision regarding the current booking."
    )

    doctor_id: str | None = Field(
        default=None,
        description="The ID of the selected doctor. Required when decision is 'select_doctor', otherwise null."
    )

qwen35 = container.qwen_35()

qwen35_with_structured_output = qwen35.with_structured_output(BookingDecision)

async def post_choose_doctor(state):

    system_message = SystemMessage(content="""
Determine the user's decision regarding the currently proposed doctor.

Return one of:
- "select_doctor": User accepts/selects the doctor and wants to proceed with booking.
- "modify_criteria": User wants another doctor or wants to change search criteria.
- "cancel_booking": User wants to stop the booking process.

If "select_doctor", return the selected doctor's ID.
Otherwise, doctor_id must be null.

Do not infer a decision from ambiguous messages.
""")

    llm_input = [system_message, state['messages'][-1]]

    res = await qwen35_with_structured_output.ainvoke(llm_input)

    return {"doctor_choice": {"choice": res.decision, "doctor_id": res.doctor_id}}


async def decide_choose_ask_date(state):
    
    if state['doctor_choice']['choice'] == "select_doctor" and state['chosen_date']:
        return "book_appointment"
    elif state['doctor_choice']['choice'] == "cancel_booking":
        return "cancel_booking"
    else:
        return "ask_date"



if __name__ == "__main__":
    pass