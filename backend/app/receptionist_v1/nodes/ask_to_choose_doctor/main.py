
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.container import container
from typing import Literal
from pydantic import BaseModel, Field
from langgraph.types import interrupt

class BookingDecision(BaseModel):
    # decision: Literal[
    #     "select_doctor",
    #     "modify_criteria",
    #     "cancel_booking",
    # ] = Field(
    #     description="The user's decision regarding the current booking."
    # )
    
    id: int | None = Field(
        default=None,
        description="The ID of the selected doctor. Return only the id, and nothing else."
    )


qwen35 = container.qwen_35()
qwen35_with_structured_output = qwen35.with_structured_output(BookingDecision)

async def ask_to_choose_doctor(state):
    print("NODE: ask_to_choose_doctor")

    context = ""
    for idx, payload in enumerate(state['location_filtered_payloads'], start=1):
        context += f"دکتر شماره {idx}"
        context += f"id: {payload["id"]} | "
        context += f"Doctor: {payload['name']} | "
        context += f"Profession: {payload['profession']} | "
        context += f"availability: {payload['availability']}"
        context += "\n\n"
 

    if len(state['location_filtered_payloads']) == 1:
        content = f"""You are a clinic receptionist. Your primary language is Persian.
Available doctor in the user's city ({state['patient_info']['city']}):
{context}

- DO NOT greet the user.
- Keep a formal, concise tone.
- Be direct and on point.
- There is only ONE doctor available with this profession. Ask the user if they would like to choose this doctor.
"""
    else:
        content = f"""You are a clinic receptionist. Your primary language is Persian.
Available doctors in the user's city ({state['patient_info']['city']}):
Number of available doctors: {len(state['location_filtered_payloads'])}
{context}

- DO NOT greet the user.
- Keep a formal, concise tone.
- Be direct and on point.
- Only show doctors from the user's city.
- User must choose one doctor from the list.
""" # TODO WE CAN SEND THE REST OF DOCTOR's Profile as well. as a expandable button.
#     # THis prompt must be revised, the llm says stuff of its own.
#     system_message = SystemMessage(content=f"""Ask user to choose a doctor among the ones below:
# {context}                                 
# """)
    
    ai_question = await qwen35.ainvoke(content)
    # print(ai_question.content)

    # print("ASK TO CHOOSE DOCTOR INTERRUPT HAPPENED.")
    # human_input = interrupt(ai_question)


    return {"messages": [ai_question]}

async def post_ask_to_choose_doctor(state):
    
    if state["route_decision"]['doctor_name']:
        return "book_appointment"
    else:
        return "END"

    # print("CONTENT: ", content)
    # print("RES: ", ai_question.content)
 
    # INTERRUPT! Execution pauses here

    print("INTERRUPTION HAPPENED.")
    human_response = interrupt(ai_question.content)
    print(human_response)
    # human response will be, something like: من دکتر چن رو انتخاب می کنم.

    system_message = SystemMessage(content="""Extract the id value.
example: id: 2 | Doctor: دکتر مایکل چن | Profession: متخصص مغز و اعصاب
output: 2
example: id: 47 | Doctor: دکتر سارا جونز | Profession:  جراحی فک و دندان
output: 47
example: id: 151 | Doctor: دکتر ابراهیم زارع | Profession:  روانشناسی بالینی
output: 151""")

    context_as_ai_message = AIMessage(content=context)
    print("context_as_ai_message", context_as_ai_message)
    llm_input = [system_message, context_as_ai_message, HumanMessage(content=human_response)]
    
    res = await qwen35_with_structured_output.ainvoke(llm_input)

    print(res)
    chosen_doctor = None
    for payload in state["location_filtered_payloads"]:
        
        if payload['id'] == res.id:
            chosen_doctor = payload

    print(chosen_doctor['name'])
    return {"messages": [ai_question, HumanMessage(content=human_response)], "chosen_doctor": chosen_doctor}




if __name__ == "__main__":
    asyncio.run(ask_to_choose_doctor({}))