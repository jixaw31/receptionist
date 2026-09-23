from app.container import container
from qdrant_client.models import Document
from langchain_core.messages import SystemMessage, AIMessage
qdrant = container.qdrant_client()
qwen35 = container.qwen_35()

# Format doctor info for the system message
def format_doctor_for_prompt(doctor_data: dict) -> str:
    """Format doctor information for system prompt"""
    
    fields = {
        'name': 'Name',
        'profession': 'Specialty',
        'title': 'Title',
        'description': 'Description',
        'specialties': 'Specialties',
        'experience_years': 'Years of Experience',
        'education': 'Education',
        'hospital': 'Hospital',
        'location': 'Location',
        'rating': 'Rating',
        'consultation_fee': 'Consultation Fee',
        'phone': 'Phone',
        'email': 'Email',
        'is_accepting_patients': 'Accepting Patients',
        'languages': 'Languages',
        'availability': 'Working Days'
    }
    
    lines = ["Doctor Information:", "=" * 40]
    
    for key, label in fields.items():
        if key in doctor_data and doctor_data[key] is not None:
            value = doctor_data[key]
            
            if value == "" or value == []:
                continue
            
            if isinstance(value, list):
                value = " • " + "\n • ".join(value)
            elif key == 'is_accepting_patients':
                value = "Yes" if value else "No"
            elif key == 'rating':
                value = f"{value} ⭐"
            elif key == 'consultation_fee':
                value = f"{value:,} Toman"
            elif key == 'experience_years':
                value = f"{value} years"
                
            lines.append(f"{label}: {value}")
    
    if 'schedule' in doctor_data and doctor_data['schedule']:
        lines.append("\nWeekly Schedule:")
        schedule = doctor_data['schedule']
        for day, times in schedule.items():
            lines.append(f"  {day}: {times['start']} - {times['end']} ({times['slots']} slots)")
    
    lines.append("=" * 40)
    return "\n".join(lines)





async def search_doctor_by_name(state):
    print("NODE: search_doctor_by_name")
    doctor_name = state['route_decision']['doctor_name']
    # bm25 search happens here.
    res = await qdrant.query_points(
        collection_name="doctors",
        query=Document(
            text=doctor_name,
            model="qdrant/bm25",
        ),
        using="bm25",
        limit=1,
    )
    if len(res.points) == 0:
        print(f"NO DOCTOR NAMED: {doctor_name} found.")
        ai_failed_response = AIMessage(content=f"دکتری به این نام  پیدا نشد.")
        return {"messages": [ai_failed_response], "delete_ai_message_id": ai_failed_response.id}
    else:
        # print("FETCHED_BY_NAME_DOCTOR_INFO: ", format_doctor_for_prompt(doctor_info))
        
        # print(res.content)
        return {"fetched_doctor_info": res.points[0].payload}


async def post_search_doctor_by_name(state):

    if state["patient_info"]["name"] and state['patient_info']['phone_number'] and state['patient_info']['city'] and \
          state['patient_info']['day']:
        return "book_appointment"
    elif "delete_ai_message_id" in state:
        return "delete_ai_message"
    else:
        return "ask_patient_info"









if __name__ == "__main__":
    pass