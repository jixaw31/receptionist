from langchain_core.messages import AIMessage

async def post_post_book_appointment(state):
    response = AIMessage(
        content="تایید شد." if state["confirmation"] else "تایید نشد."
    )
    return {"messages": [response]}
