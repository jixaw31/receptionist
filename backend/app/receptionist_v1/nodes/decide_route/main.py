from .system_message import system_message, UserIntent, gather_info_system_message, UserInfo
from app.container import container
from provinces_and_cities import Iran

qwen35 = container.qwen_35()
qwen35_with_structured_output = qwen35.with_structured_output(UserIntent)
qwen35_with_structured_output_user_info = qwen35.with_structured_output(UserInfo)

async def decide_route(state):
    print("NODE: decide_route")
    


    for m in state['messages']:

        print(m.type.upper(), m.content)
        print("---------------------------------")
    
    if "patient_info" not in state:
        patient_info_dict = {
            "phone_number": None, "name": None, 
            "city":None, "province": None, "day": None, 
            "time": None,
        }
    else:
        patient_info_dict = state['patient_info']
    
    patient_info_res = await qwen35_with_structured_output_user_info.ainvoke(
        [gather_info_system_message] + [m for m in state["messages"] if m.type=="human"]
    )

    print(patient_info_res)

    current_info = patient_info_dict

    city = patient_info_res.city or current_info["city"]
    name = patient_info_res.name or current_info["name"]
    phone_number = patient_info_res.phone_number or current_info["phone_number"]
    day = patient_info_res.day or current_info["day"]
    time = patient_info_res.time or current_info["time"]
    
    # Find province from city
    province_name = current_info.get("province")

    if city:
        for province in Iran.all:
            if city in province["cities"]:
                province_name = province["name"]
                break

    patient_info_dict = {
        "name": name, "city": city, "province": province_name, "day": day, 
        "time": time, "phone_number": phone_number,
    }
   

    res = await qwen35_with_structured_output.ainvoke([system_message] + state['messages'])
    print(res)
    
    print({
        "route_decision": {"decision": res.category, "doctor_name": res.doctor_name, "intention": res.intent},
        "patient_info": patient_info_dict,
        
    })
    chosen_doctor = res.doctor_name

    return {
        "route_decision": {"decision": res.category, "doctor_name": res.doctor_name, "intention": res.intent},
        "patient_info": patient_info_dict,
    }



async def classifier(state):
    
    for item in ["casual", "look_for_doctor", "doctor_exists"]:
        if state['route_decision']['decision'] == item:
            return item




if __name__ == "__main__":
    pass