
import streamlit as st
#from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import chat1, chat2, mysql_agent_prompt_improved, environment_prompt_template, process_task_environment, play_from_point, chat_bubble, add_message
from copy import deepcopy
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import re
import pickle

load_dotenv() 
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

model = ChatOpenAI(model="gpt-4-0613")
model.temperature = 0.8

environment_model = ChatOpenAI(model="gpt-4-0613")
model.temperature = 0.8

# Initialize a session state to store the conversation
if 'agent_messages' not in st.session_state:
    st.session_state.agent_messages = deepcopy(chat1)
# Initialize a session state to store the conversation
if 'environment_messages' not in st.session_state:
    st.session_state.environment_messages = deepcopy(chat2)

# Add a state variable for edit mode
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = {"agent":{}, "environment":{}}

# Add a state variable to store temporary edited text
if 'edited_text' not in st.session_state:
    st.session_state.edited_text = {"agent":{}, "environment":{}}

# Initialize the session state variable if it's not already set
if 'workspace' not in st.session_state:
    st.session_state.workspace= None

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# Initialize session state
if 'num_examples' not in st.session_state:
    st.session_state.num_examples = 0

# Initialize session state
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False



# Function to update the current index
def update_index(direction):
    index = st.session_state.current_index
    st.session_state.workspace['agents'][index] = st.session_state['agent_messages']
    st.session_state.workspace['environments'][index] = st.session_state['environment_messages']
    if direction == 'left':
        index = (index - 1) % st.session_state.num_examples
    elif direction == 'right':
        index = (index + 1) % st.session_state.num_examples
    st.session_state['agent_messages'] = st.session_state.workspace['agents'][index]
    st.session_state['environment_messages'] = st.session_state.workspace['environments'][index]
    st.session_state.current_index = index 


def main():
    st.set_page_config(layout="wide")
    st.title("Synchaev")
    # Create a chat conversation from chat1 and display it
    offset = 3
    max_length = max(len(st.session_state.agent_messages), len(st.session_state.environment_messages))
    
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
                if index < len(st.session_state.agent_messages):
                    message = st.session_state.agent_messages[index]
                    chat_bubble(st, "agent", index, message.type, message.content)
                else:
                    # Placeholder for alignment
                    st.write("")  # Adjust this to better match your app's design

            # Environment Conversation
            with col2:
                if index < offset:
                    #chat_bubble("environment", index, "ai", "", is_placeholder=True)
                    st.write("")
                if index >= offset and (index - offset) < len(st.session_state.environment_messages):
                    message = st.session_state.environment_messages[index-offset]
                    chat_bubble(st, "environment", index+offset, message.type, message.content)
                else:
                    # Placeholder for alignment
                    st.write("")  # Adjust this to better match your app's design

        # Additional code for adding messages, etc.
    with row:
        col1, col2 = st.columns([5, 5])  # Adjust column widths as needed
        with col1:
            if st.button('➕', key=f'agent_add'):
                add_message(st, "agent")
        with col2:
            if st.button('➕', key=f'environment_add'):
                add_message(st, "environment")
    

    with st.container():
        # Horizontal bar to set off the navigation section
        st.markdown("---")

        # Adjusted layout for buttons and current example display
        col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1, 1.5, 1])
        with col2:
            if st.button('← Previous'):
                update_index('left')
                st.rerun()
        with col3:
            # Display the current example number and total
            if st.session_state.workspace:
                st.write(f"{st.session_state.current_index + 1} of {st.session_state.num_examples}")
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
                    st.session_state.workspace = pickle.load(uploaded_file)
                    st.session_state.num_examples = len(st.session_state.workspace["agents"])
                    st.session_state.file_processed = True
                    # Display a success message
                    st.success("Pickle file loaded successfully!")
                    # Load Index 1
                    st.session_state['environment_messages'] = st.session_state.workspace["environments"][0]
                    st.session_state['agent_messages'] = st.session_state.workspace["agents"][0]
                    st.rerun()

                except Exception as e:
                    st.error(f"An error occurred: {e}")
            
            # Reset the file_processed state if the user uploads a new file
            if st.button('Upload New File'):
                st.session_state.file_processed = False
                st.rerun()

if __name__ == "__main__":
    main()
