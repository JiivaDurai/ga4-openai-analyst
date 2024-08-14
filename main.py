
from function_schema import tools
from bigquery_functions import execute_sql_query, get_table_schema
import streamlit as st
from open_ai import client, assistant_id
from open_ai import EventHandler



# Streamlit app layout
st.title("Bigquery SQL Assistant with Function Calling")

# Input box for user queries
text_box = st.empty()


# Initialize chat history in session state if not already done
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if "assistant_text" not in st.session_state:
    st.session_state.assistant_text = [""]

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "text_boxes" not in st.session_state:
    st.session_state.text_boxes = []

def display_chat_history():
    for role, content in st.session_state.chat_history:
        if role == "user":
            st.chat_message("User").write(content)
        else:
            st.chat_message("Assistant").write(content)

display_chat_history()

if prompt := st.chat_input("Enter your message"):
    # query_extra = f"This is the users details for the query request if the user asks any question on SQL \
    #     \n User details: \n User ID: Kasamuki \n User Name: Potato Chips \n \
    #         User dataset: cl3967trkvbts3, Tablename: events_202309" 
    st.session_state.chat_history.append(("user", prompt))

    # Assuming the user input is related to calculating tax
    # if "tax" in prompt.lower():  # You can adjust this condition based on your actual use case
    #     try:
    #         tax_result = calculate_tax(prompt)  # Assuming prompt contains revenue
    #         st.session_state.chat_history.append(
    #             ("assistant", f"Tax for revenue {tax_result['revenue']}: {tax_result['tax']}"))
    #     except ValueError as e:
    #         st.session_state.chat_history.append(("assistant", str(e)))
    

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt,        
    )

    st.session_state.text_boxes.append(st.empty())
    st.session_state.text_boxes[-1].success(f" {prompt}")

    with client.beta.threads.runs.stream(thread_id=st.session_state.thread_id,
                                         assistant_id=assistant_id,
                                         event_handler=EventHandler(),
                                         temperature=0) as stream:
        stream.until_done()
