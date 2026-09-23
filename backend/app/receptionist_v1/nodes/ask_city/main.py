
from app.container import container
from langchain_core.messages import SystemMessage

qwen35 = container.qwen_35()


async def ask_city(state):
    
    if state['patient_info']['city']:
        pass
    else:
        print("NODE: ask_city")
        system_message = SystemMessage(content="Ask user for their current city of residence, brief and concise.")
        content="Ask user for their current city of residence, brief and concise. Primary language is Persian, unless user speeks another language."
        res = await qwen35.ainvoke(content)
 
        print(res.content)
        return {"messages": [res]}
    
async def post_ask_city(state):
    if state['patient_info']['city']:
        return "convert_query"
    else:
        return "END"