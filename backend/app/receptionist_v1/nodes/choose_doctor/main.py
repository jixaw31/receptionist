
import asyncio
from langgraph.types import interrupt



async def choose_doctor(state):
    print("NODE: choose_doctor")

        
    # -----------------------------------------------------------------
    # INTERRUPT: Human reviews candidate doctors before booking
    # -----------------------------------------------------------------
    interrupt_data = state['before_doctor_choice_interrupt']

    

    # INTERRUPT! Execution pauses here
    human_response = interrupt(interrupt_data)
    
    # When resumed, human_response contains the human's decision
    print(f"\n👤 Human response received: {human_response}")
     
    chosen_doctor = None
    if human_response["action"] == "select_doctor":
        
        
        for doctor in interrupt_data['candidate_doctors']:
            if doctor['id'] == int(human_response["doctor_id"]):
                
                chosen_doctor = doctor
    
        return {"chosen_doctor": chosen_doctor}
    elif human_response["action"] == "modify_criteria":
        pass # for now

    else: 
        pass


async def decide_choose_ask_date(state):
    print("POST NODE: choose doctor")
    
    if state['chosen_date']['day']:
        return "book_appointment"
    else:
        return "ask_date"


if __name__ == "__main__":
    asyncio.run(choose_doctor({}))