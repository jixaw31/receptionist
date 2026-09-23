from app.container import container
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, RemoveMessage
import asyncio

class Confirmation(BaseModel):
    result: bool 
    

qwen35 = container.qwen_35()
qwen35_with_structured_output = qwen35.with_structured_output(Confirmation)

async def post_book_appointment(state):
    print("NODE: post_book_appointment")

    system_message = SystemMessage(content="""
You are a confirmation classifier.

Determine whether the user's LAST message explicitly approves or rejects the proposed appointment.

Return:
- result = true ONLY if the user clearly accepts, confirms, or approves the appointment.
- result = false if the user rejects, declines, cancels, says no, or does not clearly approve.

IMPORTANT:
- "no", "نه", "خیر", "نمی‌خوام", "لغو کن", "cancel", "don't", "do not" → false
- "yes", "بله", "آره", "حتما", "باشه", "تایید", "تأیید", "اوکی", "sure", "yes please" → true
- Do NOT interpret a question as approval.
- Do NOT infer approval merely because the user continues talking about the appointment.
- If the user's intent is ambiguous or unclear, return false.
- Evaluate ONLY the user's last message.
""")

    res = await qwen35_with_structured_output.ainvoke([
        system_message,
        state["messages"][-1],
    ])
    
    return {"confirmation" : res.result}


if __name__ == "__main__":
    res = asyncio.run(post_book_appointment({"messages": [HumanMessage(content="بله")]}))
    print(res)