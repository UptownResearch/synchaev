import streamlit as st
#from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import chat_bubble, model, environment_model, creator_model
from copy import deepcopy
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import re
import pickle
from chatcontents import DBBenchChatContent, OSChatContent, AlfChatContent, KGChatContent, M2WChatContent, WSChatContent
from prompts import *

load_dotenv() 

# Function to update the current index
def update_index(direction):
    index = st.session_state.example_index
    if direction == 'left':
        index = (index - 1) % st.session_state.cc.num_examples()
    elif direction == 'right':
        index = (index + 1) % st.session_state.cc.num_examples()
    st.session_state.example_index = index 

# Function to update the current index
def delete_index():
    index = st.session_state.example_index
    st.session_state.cc.delete_example(index)
    index = index % st.session_state.cc.num_examples()
    st.session_state.example_index = index 



def main(agentbench_split):
    # Add a state variable for edit mode
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = {"agent":{}, "environment":{}}

    # Add a state variable to store temporary edited text
    if 'edited_text' not in st.session_state:
        st.session_state.edited_text = {"agent":{}, "environment":{}}

    # Initialize the session state variable if it's not already set
    if 'workspace' not in st.session_state:
        st.session_state.workspace= None

    if 'example_index' not in st.session_state:
        st.session_state.example_index = 0

    if 'num_examples' not in st.session_state:
        st.session_state.num_examples = 0

    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False

    if 'file_location' not in st.session_state:
        st.session_state.file_processed = False

    if 'cc' not in st.session_state:
        if agentbench_split == "dbbench":
            # Initialize a session state to store the conversation
            st.session_state.agent_messages = deepcopy(db_chat1)
            # Initialize a session state to store the conversation
            st.session_state.environment_messages = deepcopy(db_chat2)
            st.session_state.cc = DBBenchChatContent(model, environment_model, creator_model)
            inital = {
                    "agents": [db_chat1],
                    "environments": [db_chat2]
            }
        elif agentbench_split == "os":
            # Initialize a session state to store the conversation
            st.session_state.agent_messages = deepcopy(os_chat1)
            # Initialize a session state to store the conversation
            st.session_state.environment_messages = deepcopy(os_chat2)
            st.session_state.cc = OSChatContent(model, environment_model, creator_model)
            inital = {
                    "agents": [os_chat1],
                    "environments": [os_chat2]
            }
        elif agentbench_split == "alfworld":
            # Initialize a session state to store the conversation
            st.session_state.agent_messages = deepcopy(alf_chat1)
            # Initialize a session state to store the conversation
            st.session_state.environment_messages = deepcopy(alf_chat2)
            st.session_state.cc = AlfChatContent(model, environment_model, creator_model)
            inital = {
                    "agents": [alf_chat1],
                    "environments": [alf_chat2]
            }
        elif agentbench_split == "kg":
            # Initialize a session state to store the conversation
            st.session_state.agent_messages = deepcopy(kg_chat1)
            # Initialize a session state to store the conversation
            st.session_state.environment_messages = deepcopy(kg_chat2)
            st.session_state.cc = KGChatContent(model, environment_model, creator_model)
            inital = {
                    "agents": [kg_chat1],
                    "environments": [kg_chat2]
            }
        elif agentbench_split == "mind2web":
            # Initialize a session state to store the conversation
            st.session_state.agent_messages = deepcopy(m2w_chat1)
            # Initialize a session state to store the conversation
            st.session_state.environment_messages = deepcopy(m2w_chat2)
            st.session_state.cc = M2WChatContent(model, environment_model, creator_model)
            inital = {
                    "agents": [m2w_chat1],
                    "environments": [m2w_chat2]
            }
        elif agentbench_split == "webshop":
            # Initialize a session state to store the conversation
            st.session_state.agent_messages = deepcopy(ws_chat1)
            # Initialize a session state to store the conversation
            st.session_state.environment_messages = deepcopy(ws_chat2)
            st.session_state.cc = KGChatContent(model, environment_model, creator_model)
            inital = {
                    "agents": [ws_chat1],
                    "environments": [ws_chat2]
            }
        else:
            NotImplementedError
        st.session_state.cc.load(inital)
        
    st.set_page_config(layout="wide")
    st.title("Synchaev")
    # Create a chat conversation from chat1 and display it
    offset = 3
    max_length = st.session_state.cc.max_chat_length(st.session_state.example_index)
    
    row = st.container()
    with row:
        col1, col2 = st.columns([5, 5])  # Adjust column widths as needed
        with col1:
            st.header("Agent")
        with col2:
            st.header("Environment")
            
    for index in range(max_length):
        # Create a row for each pair of messages

        row = st.container()
        with row:
            col1, col2 = st.columns([5, 5])  # Adjust column widths as needed

            # Agent Conversation
            with col1:
                message = st.session_state.cc.get_agent_side(st.session_state.example_index, index)
                chat_bubble(st, "agent", index, message.type, message.content, is_placeholder=True if hasattr(message, 'is_placeholder') else False)
            # Environment Conversation
            with col2:
                message = st.session_state.cc.get_environment_side(st.session_state.example_index, index)
                chat_bubble(st, "environment", index, message.type, message.content, is_placeholder=True if hasattr(message, 'is_placeholder') else False)


        # Additional code for adding messages, etc.
    with row:
        col1, col2 = st.columns([5, 5])  # Adjust column widths as needed
        with col1:
            if st.button('➕', key=f'agent_add'):
                st.session_state.cc.add_to_agent(st.session_state.example_index)
                st.rerun()
        with col2:
            if st.button('➕', key=f'environment_add'):
                st.session_state.cc.add_to_environment(st.session_state.example_index)
                st.rerun()
    
    with st.container():
        # Horizontal bar to set off the navigation section
        st.markdown("---")
        # Adjusted layout for buttons and current example display
        col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1, 1.5, 1])
        with col3:
            if st.button('Delete'):
                st.session_state.cc.delete_example(st.session_state.example_index)
                st.rerun()


    with st.container():
        # Adjusted layout for buttons and current example display
        col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1, 1.5, 1])
        with col2:
            if st.button('← Previous'):
                update_index('left')
                st.rerun()
        with col3:
            # Display the current example number and total
            st.write(f"{st.session_state.example_index+ 1} of {st.session_state.cc.num_examples()}")
        with col4:
            if st.button('Next →'):
                update_index('right')
                st.rerun()

    with st.container():
        # Adjusted layout for buttons and current example display
        col1, col2, col3 = st.columns([2, 2, 2])
        with col2:
            uploaded_file = st.file_uploader("Choose a file")

            if uploaded_file is not None and not st.session_state.file_processed:
                try:
                    # Deserialize the file content
                    filecontents = pickle.load(uploaded_file)
                    if agentbench_split == "dbbench":
                        st.session_state.cc = DBBenchChatContent(model, environment_model, creator_model)
                    elif agentbench_split == "os":
                        st.session_state.cc = OSChatContent(model, environment_model, creator_model)
                    elif agentbench_split == "alfworld":
                        st.session_state.cc = AlfChatContent(model, environment_model, creator_model)
                    elif agentbench_split == "kg":
                        st.session_state.cc = KGChatContent(model, environment_model, creator_model)
                    elif agentbench_split == "mind2web":
                        st.session_state.cc = M2WChatContent(model, environment_model, creator_model)
                    elif agentbench_split == "webshop":
                        st.session_state.cc = WSChatContent(model, environment_model, creator_model)
                    else:
                        NotImplementedError
                    st.session_state.cc.load(filecontents)
                    st.session_state.file_processed = True
                    st.session_state['file_location'] = uploaded_file
                    # Display a success message
                    st.success("Pickle file loaded successfully!")
                    st.session_state.example_index = 0
                    st.rerun()

                except Exception as e:
                    st.error(f"An error occurred: {e}")
            
            # Reset the file_processed state if the user uploads a new file
            if st.button('Open File'):
                st.session_state.file_processed = False
                st.rerun()

            # Interface to input the file name
            file_name = st.text_input("Enter the name of the file to save to (with .pickle extension):")

            # Button to save the input to a pickle file
            if st.button('Save to pickle file'):
                if file_name:
                    # Saving data to the specified pickle file
                    st.session_state.cc.write(file_name)
                else:
                    st.error("Please enter a file name.")

if __name__ == "__main__":
    agentbench_split = "mind2web" # choices: ["dbbench", "os", "alfworld", "kg", "mind2web", "webshop"]
    main(agentbench_split)
