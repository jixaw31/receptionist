from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from app.container import container
from provinces_and_cities import Iran
from langgraph.types import interrupt

class PatientCity(BaseModel):
    city: str | None = Field(
        default=None,
        description=(
            "The city of residence of the patient. "
            "Return None if the conversation does not provide a city."
        )
    )
    

gather_city_system_message = SystemMessage(
        content="""
Extract patient information from the conversation.

Extract the following field:
- city: The patient's city of residence, only if explicitly provided.


Rules:
- Only extract information about the patient's city explicitly stated in the conversation.
"""
    )

qwen35 = container.qwen_35()
qwen35_with_structured_output = qwen35.with_structured_output(PatientCity)

async def gather_city(state):
    print("NODE gather_city")
    province_name = None

    if "patient_info" not in state:

        state['patient_info'] = {"city": None, "province": None}
    
        system_message = SystemMessage(content="Ask user for their current city of residence, brief and concise.")
        res = await qwen35.ainvoke([system_message, state['messages'][-1]])

        # INTERRUPT! Execution pauses here
        human_response = interrupt(res.content)

        # human_response = something like this: ما در مشهد زندگی می کنیم.
         
        res = await qwen35_with_structured_output.ainvoke([gather_city_system_message, HumanMessage(content=human_response)])
        print(res)
        
        if res.city:
            for province in Iran.all:
                if res.city in province["cities"]:
                    province_name = province["name"]
                    break
        return {"patient_info": {"city": res.city, "province": province_name}}
        # return {"messages": [res]}

    else:
        if "city" in state['patient_info'] and state['patient_info']['city']:
            city = state['patient_info']['city']
            
            for province in Iran.all:
                if state['patient_info']['city'] in province["cities"]:
                    province_name = province["name"]
                    break
        else:
            res = await qwen35_with_structured_output.ainvoke([gather_city_system_message] + state['messages'])
            print(res)
            city = res.city
            if city:
                for province in Iran.all:
                    if res.city in province["cities"]:
                        province_name = province["name"]
                        break
        print({"patient_info": {"city": city, "province": province_name}})
        return {"patient_info": {"city": city, "province": province_name}}


# async def post_gather_city(state):

#     if state['patient_info']['city']:
#         return "convert_query" 
#     else:
#         return "ask_city"

