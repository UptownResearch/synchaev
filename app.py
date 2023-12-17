
import streamlit as st
#from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import chat1, chat2, mysql_agent_prompt_improved, environment_prompt_template, process_task_environment, play_from_point
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

# Function to add a message to the conversation
def add_message(st, conversation):
    if conversation == "agent":
        if st.session_state['agent_messages'][-1].type == "ai":
            return
        else:
            agent_response = model.predict_messages(st.session_state['agent_messages'])
            st.session_state['agent_messages'].append(agent_response)
            print(agent_response.content + "\n")
            sql_block = re.search(r"```sql(.*?)```", agent_response.content, re.DOTALL)
            if sql_block:
                sql_code = sql_block.group(1).strip()
            else:
                sql_code = ""
            if not "Final Answer:" in agent_response.content:
                st.session_state['environment_messages'].append(HumanMessage(content=sql_code))
            st.rerun()       

    else:
        if st.session_state['environment_messages'][-1].type == "ai":
            return
        else:
            environment_result = environment_model.predict_messages(st.session_state['environment_messages'])
            st.session_state['environment_messages'].append(environment_result)
            print(environment_result.content)
            st.session_state['agent_messages'].append(HumanMessage(content=environment_result.content))
            st.rerun()



# Modified chat_bubble function
def chat_bubble(conversation, index, participant, text, is_placeholder=False):
    avatar = "🤖" if participant.lower() == "ai" else "🌍"
    if is_placeholder:
        avatar = None
    with st.container():
        # Check if the message is in edit mode
        if st.session_state.edit_mode[conversation].get(index, False):
            # Render text input for editing
            # Calculate the number of lines in the text
            number_of_lines = text.count('\n') + 1  # Adding 1 for the last line if it doesn't end with a newline

            # Estimate the height based on the number of lines
            # You may need to adjust the multiplier based on your specific layout and font size
            estimated_height_per_line = 40  # Example height in pixels per line
            estimated_height = number_of_lines * estimated_height_per_line + 100

            # Use st.text_area with the calculated height
            st.session_state.edited_text[conversation][index] = st.text_area("Edit Message", value=text, key=f'edit_{index}', height=estimated_height)   
            if st.button('Save', key=f'save_{index}'):
                # Save logic here
                if conversation == 'agent':
                    st.session_state['agent_messages'][index].content = st.session_state.edited_text[conversation][index]
                else:
                    st.session_state['environment_messages'][index].content = st.session_state.edited_text[conversation][index]
                st.session_state.edit_mode[conversation][index] = False
                st.rerun()
        else:
            # Render chat message
            with st.chat_message(name=participant, avatar=avatar):
                st.write(text)

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([4, 1, 1, 1, 1])
            with col1:
                    pass
            with col2:
                if participant.lower() == "ai":
                    if st.button('▶️', key=f'{conversation}_play_{index}'):
                        play_from_point(st, model, model, conversation, index, participant)
                        st.rerun()
            with col3:    
                if participant.lower() == "ai":
                    if st.button('🔄', key=f'{conversation}_refresh_{index}'):
                        if conversation == "agent":
                            agent_response = model.predict_messages(st.session_state['agent_messages'][:index])
                            print(agent_response)
                            st.session_state['agent_messages'][index] = agent_response
                            st.rerun()
                            
                        else:
                            environment_result = environment_model.predict_messages(st.session_state['environment_messages'][:index])
                            print(environment_result)
                            st.session_state['environment_messages'][index] = environment_result
                            st.rerun()
            with col4:
                if st.button('✏️', key=f'{conversation}_edit_{index}'):
                    # Toggle edit mode
                    st.session_state.edit_mode[conversation][index] = not st.session_state.edit_mode[conversation].get(index, False)
                    st.rerun()
            with col5:
                if participant.lower() == "ai":
                    if st.button('🗑️',  key=f'{conversation}_delete_{index}'):
                        # Delete the message
                        if conversation == 'agent':
                            del st.session_state['agent_messages'][index:]
                            if index <= 3:
                                del st.session_state['environment_messages']
                            if index > 3:
                                del st.session_state['environment_messages'][index-3:]
                        else:
                            print("Delete clicked in Environment")
                            del st.session_state['environment_messages'][index:]
                            del st.session_state['agent_messages'][index+3:]
                        st.rerun()



# Function to update the current index
def update_index(direction):
    if direction == 'left':
        st.session_state.current_index = (st.session_state.current_index - 1) % len(st.session_state.examples)

    elif direction == 'right':
        st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.examples)



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
                    chat_bubble("agent", index, message.type, message.content)
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
                    chat_bubble("environment", index+offset, message.type, message.content)
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
        with col3:
            # Display the current example number and total
            if st.session_state.workspace:
                st.write(f"{st.session_state.current_index + 1} of {st.session_state.num_examples}")
        with col4:
            if st.button('Next →'):
                update_index('right')

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
