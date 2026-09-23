from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field



def get_ask_patient_info_system_message(name, phone_number, city, day, hour, availability, doctor_name):
    doctor_info = ""
    if doctor_name:
        doctor_info = f"""
Always mention the doctor available below:
Doctor's name: {doctor_name}
Doctor's Weekly Schedule: {availability}"""
    return SystemMessage( content=f"""Ask the user for the following missing patient information:
- The patient's full name.
- A phone number for future contact.
- City of the residence.
- Desired date and time.       

             
{doctor_info}            

The user may be speaking on behalf of themselves or another patient.

Ask naturally and clearly for both pieces of information.
Use the same language as the user.

- Only ask the missing information.

current information about user that we have:
name: {name}
phone_number: {phone_number}
city: {city}
patient_desired_day: {day}
patient_desired_hour: {hour}
""")

gather_info_system_message = SystemMessage(
    content=f"""Extract patient information from the conversation.

Extract the following fields independently:

- patient_name: The patient's full name, only if explicitly provided.
- city: The patient's city of residence, only if explicitly provided.
- phone_number: The patient's phone number.
- Date and time: The patient's desired date and time.

Rules:
- A valid patient full name should be a must be proper personal name.
- Extract the patient name as: FirstName LastName
- Either field may be present without the other.
- All fields may be present.
- Neither field may be present.
- Only extract information explicitly stated in the conversation.
- Never guess, infer, or fabricate information.
- If a field is not explicitly provided, return None for that field.
"""
    )

class UserInfo(BaseModel):
    city: str | None = Field(
        default=None,
        description=(
            "The city of residence of the patient. "
            "Return None if the conversation does not provide a city."
        )
    )
    name: str | None = Field(
        default=None,
        description=(
            "The full name of the patient."
            "Return None if the conversation does not provide the name of the patient."
            "Sometime the user you are interacting with may not be the patient, he/she might be reserving an appointment for someone else."
        )
    )
    phone_number: str | None = Field(
        default=None,
        description=(
            "The patient's phone number."
        )
    )
    date_time: str | None = Field(
        default=None,
        description=(
            "The patient's desired date and time."
        )
    )