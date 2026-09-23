
from app.container import container
import asyncio
from .system_message import get_ask_patient_info_system_message, gather_info_system_message, UserInfo

from provinces_and_cities import Iran


qwen35 = container.qwen_35()

qwen35_with_structured_output_user_info = qwen35.with_structured_output(UserInfo)


async def ask_patient_info(state):
    print("NODE ask_patient_info")
    

    # Check if all values exist (not None, not empty)
    all_valid = all(value is not None and value != "" for value in state['patient_info'].values())
    if all_valid:
        print("all_valid -> PASSED")        
    else:
        ask_patient_info_system_message = get_ask_patient_info_system_message(
            state['patient_info']['name'],
            state['patient_info']['phone_number'], 
            state['patient_info']['city'],
            state['patient_info']['day'],
            state['patient_info']['time'],
            state['fetched_doctor_info']['availability'],
            state['fetched_doctor_info']['name'],
        )

        res = await qwen35.ainvoke([ask_patient_info_system_message] + state['messages'])
        
        print(res.content)


        return {"messages": [res]}

        


if __name__ == "__main__":
    asyncio.run(ask_patient_info({}))