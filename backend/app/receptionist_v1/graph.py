from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import os, asyncio
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langgraph.types import Command

from .schemas import MyMessagesState
from .nodes.call_model.main import call_model
from .nodes.decide_route.main import decide_route, classifier
from .nodes.call_casual_model.main import call_casual_model
from .nodes.helper_nodes import *
from .nodes.query_converter.main import convert_query
from .nodes.ask_to_choose_doctor.main import ask_to_choose_doctor, post_ask_to_choose_doctor
from .nodes.search.main import search
from .nodes.rerank.main import rerank
from .nodes.ask_patient_info.main import ask_patient_info
from .nodes.decide_search_doctor.main import decide_search_doctor
from .nodes.decide_gather_user_info.main import decide_gather_user_info
from .nodes.gather_patient_info.main import gather_patient_info
from .nodes.choose_date.main import choose_date, post_choose_date
from .nodes.book_appointment.main import book_appointment
from .nodes.ask_date.main import ask_date
from .nodes.post_choose_doctor.main import post_choose_doctor, decide_choose_ask_date
from .nodes.ask_city.main import ask_city, post_ask_city
from .nodes.gather_city.main import gather_city
from .nodes.post_doctor_exists.main import post_doctor_exists
from .nodes.post_book_appointment.main import post_book_appointment
from .nodes.search_doctor_by_name.main import search_doctor_by_name, post_search_doctor_by_name
from .nodes.post_post_book_appointment.main import post_post_book_appointment

async def remove_ai_message(state):
    print(f"message with ID: {state["delete_ai_message_id"]} removed.")
    return [RemoveMessage(state["delete_ai_message_id"])]

async def is_confirmed(state):
    print("CONDITIONAL: is_confirmed")
    
    # import sys;sys.exit()
    if "confirmation" in state:
        return "confirmed"
    else:
        return "decide_route"

async def create_graph(checkpointer):

    builder = StateGraph(MyMessagesState)

    builder.add_node(call_model)
    builder.add_node(call_casual_model)
    builder.add_node(decide_route)
    builder.add_node(hardcoded_response)
    builder.add_node(ask_to_choose_doctor)
    builder.add_node(remove_redundant_response)
    builder.add_node(convert_query)
    builder.add_node(search)
    builder.add_node(rerank)
    builder.add_node(ask_patient_info)
    builder.add_node(decide_search_doctor)
    builder.add_node(gather_patient_info)
    builder.add_node(choose_date)
    builder.add_node(ask_date)
    builder.add_node(book_appointment)
    builder.add_node(post_choose_doctor)
    builder.add_node(ask_city)
    builder.add_node(gather_city)
    builder.add_node(post_doctor_exists)
    builder.add_node(search_doctor_by_name)
    builder.add_node(remove_ai_message)
    builder.add_node(post_book_appointment)
    builder.add_node(post_post_book_appointment)
    

    

    builder.add_conditional_edges(
        START,
        is_confirmed,
        {
            "decide_route": "decide_route",
            "confirmed": "post_book_appointment",
            
        }
    )

    
    builder.add_conditional_edges(
        "decide_route",
        classifier,
        {
            "casual": "call_casual_model",
            "look_for_doctor": "ask_city",
            "doctor_exists": "search_doctor_by_name",
        }
    )

    builder.add_conditional_edges(
        "search_doctor_by_name",
        post_search_doctor_by_name,
        {
            "book_appointment": "book_appointment",
            "ask_patient_info": "ask_patient_info",
            "delete_ai_message": "remove_ai_message",
        }
    )

    # builder.add_edge("ask_city", "convert_query")
    builder.add_conditional_edges(
        "ask_city",
        post_ask_city,
        {
            "convert_query": "convert_query",
            "END": END,
            # "delete_ai_message": "remove_ai_message",
        }
    )

    # builder.add_edge("gather_patient_info", "book_appointment")

    # builder.add_conditional_edges(
    #     "decide_route",
    #     classifier,
    #     {
    #         "casual": "call_casual_model",
    #         "look_for_doctor": "gather_city",
    #         "doctor_exists": "convert_query",
    #     }
    # )
    
    # builder.add_edge("gather_city", "convert_query") 
    # builder.add_conditional_edges(
    #     "gather_city",
    #     post_gather_city,
    #     {
    #         "ask_city": "ask_city", # 
    #         "convert_query": "convert_query",
    #     }
    # )
    
    # builder.add_conditional_edges(
    #     "gather_user_info",
    #     decide_gather_user_info,
    #     {
    #         "ask_user_info": "ask_user_info",
    #         "decide_route": "convert_query",
    #     }
    # )
    
    builder.add_edge("convert_query", "search") 
    builder.add_edge("search", "rerank") 
    builder.add_edge("rerank", "ask_to_choose_doctor")

    builder.add_conditional_edges(
        "ask_to_choose_doctor",
        post_ask_to_choose_doctor,
        {
            "book_appointment": "book_appointment",
            "END": END,
        }
    )
    builder.add_edge("post_book_appointment", "post_post_book_appointment")
    # builder.add_edge("ask_to_choose_doctor", "choose_date")
    # builder.add_edge("book_appointment", "post_book_appointment")
    builder.add_edge("call_casual_model", "remove_redundant_response")

    # builder.add_edge("choose_doctor", "post_choose_doctor")

    # builder.add_conditional_edges(
    #     "post_choose_doctor",
    #     decide_choose_ask_date,
    #     {   
    #         "book_appointment": "book_appointment",
    #         "ask_date": "ask_date", # 
    #         "cancel_booking": END,
    #     }
    # )
    # builder.add_edge("ask_date", "choose_date")

    # builder.add_conditional_edges(
    #     "choose_date",
    #     post_choose_date,
    #     {   
    #         "ask_patient_info": "ask_patient_info",
    #         "book_appointment": "book_appointment", # 
    #     }
    # )


    

    graph = builder.compile(
        checkpointer=checkpointer,
    )
    
    return graph



load_dotenv('.env')

collection_name = "847f5e78-25b0-46b0-8188-1ebefd9c2772"
config = {"configurable": {"thread_id": collection_name}}



human_inputs_1 = ["سلام، وقتتون بخیر", "برای مادرم دنبال دکتر مغز اعصاب هستم", "ما در مشهد زندگی می کنیم.", "دکتر چن گزینه مناسبی هست.", 
                  "نیلوفر رضایی 09380075497. یکشنبه ترجیحا ساعت ۱۰.", "بله", "فرق نمی کنه لطفا اطلاعات رو ثبت کنید.", "روز یکشنبه", 
                  "sunday, 10:00.", "پنجشنبه ساعت ۸ و نیم"]

human_inputs_2 = ["سلام، وقت بخیر. پسرم یه حساسیت پوستی شدید گرفته. یه نوبت برای دکتر می‌خوام.", 
                  "به نام علی رضایی، پسرم ۷ سالشه.", "شماره تماس: ۰۹۳۵۹۸۷۶۵۴۳", "اصفهان"]

human_inputs_3 = ["سلام، وقتتون بخیر. من سه روزه درد شدید دندان دارم و صورت‌م متورم شده. هر دکتری که زنگ می‌زنم می‌گه تعطیله. لطفاً یه دکتر دندانپزشک اورژانسی پیدا کنید هرچه سریعتر.",
                  "اسم بیمار علی عباسی است.",
                  "بله. شماره من ۰۳۱-۳۳۵۵-۴۴۸۸ و در نزدیکی تهران سکونت دارم."]

human_inputs_4 = ["آیا دکتر چن وقت آزاد دارن این هفته؟", "ما در مشهد زندگی می کنیم.", "ما در مشهد زندگی می کنیم و اسم او نیلوفر رضایی است."]

human_inputs_5 = ["من یه وقت ملاقات با دکتر چن می خواستم.", "محمد علی هستم و در مشهد زندگی می کنم.  و شماره تماس من 09380075497 هست.", "ببخشید این مورد رو فراموش کردم. روز سشنبه اگر ممکن هست."]
# برای سشنبه ساعت ۱۰:۰۰ .
human_inputs_7 = ["سشنبه ساعت ۱۰:۰۰"]

human_inputs_6 = ["دکتر چن در چه حوضه ای تخصص داره؟", ""]

human_inputs_9 = ["بله"]

async def main():
    
    async with AsyncRedisSaver.from_conn_string(
        os.getenv("REDIS_URI"), 
        ttl={"default_ttl": 3600, "refresh_on_read": True}
    ) as redis_cp:
        
        graph = await create_graph(redis_cp) # Must go to container. maybe create a service out of it.

        
        for m in human_inputs_1[5:6]:
            print(m)
            result = await graph.ainvoke({
                "messages": [HumanMessage(content=m)],
                "resource_collection_name": collection_name,
                # "patient_info":{"city": "مشهد"}
            },
            config=config,
            stream_mode="values",
            )
            

            while "__interrupt__" in result:

                interrupts = result["__interrupt__"]

                for interrupt_item in interrupts:
                    print("INTERRUPTION ITEM")
                    print(interrupt_item.value)

                user_input = input("> ")

                result = None

                async for chunk in graph.astream(
                    Command(resume=user_input),
                    config=config,
                    stream_mode="values",
                ):
                    result = chunk

            
        # res_input = input("Choose select_doctor or cancel_booking")
        # if res_input == "select_doctor":
        #     doctor_id = input("enter doctor's id to proceed.")

        # human_response = {
        #     "action": res_input,
        #     "doctor_id": doctor_id,
        # }        

        # result = await graph.ainvoke(
        #     Command(resume=human_response),
        #     config=config,
        # )

        # print(result)
            
    
if __name__ == "__main__":

    asyncio.run(main())