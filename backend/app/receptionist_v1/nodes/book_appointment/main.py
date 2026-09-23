

import asyncio
from langgraph.types import interrupt
from langchain_core.messages import AIMessage
from .get_receipt import find_next_available_appointment, format_appointment_confirmation


async def book_appointment(state):
    print("NODE: book_appointment") 
    doctor = state['fetched_doctor_info']
    day = state["patient_info"]['day']
    time = state["patient_info"]["time"]

    # print(doctor)
    # print(day)
    # print(time)

    appointment = find_next_available_appointment(
        doctor=doctor,
        chosen_day=day,
        chosen_time=time,
    )

    confirmation = format_appointment_confirmation(
        doctor=doctor,
        appointment_time=appointment,
        patient_name=state['patient_info']['name'],
    )

    # print(confirmation)
    print("====================================================")
    
    # print("INTERRUPTED!")
    # human_response = interrupt(confirmation  + "\n\nآیا تایید می کنید؟")

    # print("human_response".upper(), human_response)
    res = AIMessage(content=confirmation + "\n\nآیا تایید می کنید؟")
    res.additional_kwargs["ask_confirmation"] = True
    return {"messages": [res], "confirmation": True}
    
if __name__ == "__main__":
    asyncio.run(book_appointment({}))