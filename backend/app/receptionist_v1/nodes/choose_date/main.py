
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from app.container import container
from langgraph.types import interrupt
from .system_message import system_message, a_doctor, ChosenDate

qwen35 = container.qwen_35()

qwen35_with_chosen_date_structured_output = qwen35.with_structured_output(ChosenDate)

async def choose_date(state):
    print("NODE: choose_date")

    if "chosen_date" in state and state["chosen_date"]:
        pass
 
    else:
        context = ""
        candidate_doctor = state["chosen_doctor"]
        print("candidate_doctor", candidate_doctor)
    
        context += "doctor's name: " + candidate_doctor['name'] + "\nprofession: " +  candidate_doctor['profession'] + \
        "\navailablity day: " + ", ".join(candidate_doctor['availability'])

        content=f"""You a receptionist in a clinic.
Do not greet the user, and make the questions concise.
Ask human about his/her prefered date for appointment.
Primary language is Persian, unless user speaks another.
{context}"""

        

        ai_date_question = await qwen35.ainvoke(content)

        print("DATE QUESTION INTERRUPTION HAPPENED.")
        human_response = interrupt(ai_date_question.content)

        res = await qwen35_with_chosen_date_structured_output.ainvoke([system_message, HumanMessage(content=human_response)])
        
        print(res)
        
        return {"chosen_date": {"day": res.day, "hour": res.hour}}

async def post_choose_date(state):

    if "patient_info" in state:
        print("patient info exists in state")
        if "name" not in state["patient_info"] or "phone_number" not in state['patient_info']:
            return "ask_patient_info"
        else:
            return "book_appointment"

    








if __name__ == "__main__":
    asyncio.run(choose_date({"messages": [HumanMessage(content="روز مد نظر من سشنبه است.")], "chosen_doctor": a_doctor}))