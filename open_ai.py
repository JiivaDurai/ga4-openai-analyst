from openai import OpenAI
import os
# from dotenv import load_dotenv
import ast
import streamlit as st
from openai import  AssistantEventHandler
from typing_extensions import override
from openai.types.beta.threads import Text, TextDelta
from bigquery_functions import execute_sql_query, get_table_schema

# Load environment variables from .env file

# Load the OpenAI API key from the environment variable
# set from the .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI()


# assistant = client.beta.assistants.create(
#     name="Assistant",
#     instructions="",
#     tools=tools,
#     model="gpt-4o",
# )

## Fixed assistant_id
assistant_id = "asst_9S6Eij8icii5vHcwqntwRXVL"


class EventHandler(AssistantEventHandler):
    """
    Event handler for the assistant stream
    """

    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    @override
    def on_text_created(self, text: Text) -> None:
        """
        Handler for when a text is created
        """
        # This try-except block will update the earlier expander for code to complete.
        # Note the indexing. We are updating the x-1 textbox where x is the current textbox.
        # Note how `on_tool_call_done` creates a new textbook (which is the x_th textbox, so we want to access the x-1_th)
        # This is to address an edge case where code is executed, but there is no output textbox (e.g. a graph is created)
        try:
            st.session_state[f"code_expander_{len(st.session_state.text_boxes) - 1}"].update(state="complete",
                                                                                             expanded=False)
        except KeyError:
            pass

        # Create a new text box
        st.session_state.text_boxes.append(st.empty())
        # Display the text in the newly created text box
        st.session_state.text_boxes[-1].info("".join(st.session_state["assistant_text"][-1]))

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text):
        """
        Handler for when a text delta is created
        """
        # Clear the latest text box
        st.session_state.text_boxes[-1].empty()
        # If there is text written, add it to latest element in the assistant text list
        if delta.value:
            st.session_state.assistant_text[-1] += delta.value
            #st.session_state.chat_history.append(("assistant", delta.value))
        # Re-display the full text in the latest text box
        st.session_state.text_boxes[-1].info("".join(st.session_state["assistant_text"][-1]))

    def on_text_done(self, text: Text):
        """
        Handler for when text is done
        """
        # Create new text box and element in the assistant text list
        st.session_state.text_boxes.append(st.empty())
        st.session_state.assistant_text.append("")
        st.session_state.chat_history.append(("assistant", text.value))
    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "execute_sql_query":
                try:
                    # Extract revenue from tool parameters
                    query = ast.literal_eval(tool.function.arguments)["query"]
                    # Call your calculate_tax function to get the tax
                    query_result = execute_sql_query(query)
                    # Append tool output in the required format
                    tool_outputs.append({"tool_call_id": tool.id, "output": f"{query_result}"})
                except ValueError as e:
                    # Handle any errors when calculating tax
                    tool_outputs.append({"tool_call_id": tool.id, "error": str(e)})
            elif tool.function.name == "get_table_schema":
                try:
                    # Extract revenue from tool parameters
                    dataset = ast.literal_eval(tool.function.arguments)["dataset"]
                    table_name = ast.literal_eval(tool.function.arguments)["table_name"]
                    # Call your calculate_tax function to get the tax
                    table_schema_result = get_table_schema(dataset, table_name)
                    # Append tool output in the required format
                    tool_outputs.append({"tool_call_id": tool.id, "output": f"{table_schema_result}"})
                except ValueError as e:
                    # Handle any errors when calculating tax
                    tool_outputs.append({"tool_call_id": tool.id, "error": str(e)})
        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs)

    def submit_tool_outputs(self, tool_outputs):
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=self.current_run.id,
                tool_outputs=tool_outputs,
                event_handler=EventHandler(),
        ) as stream:
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            # print()