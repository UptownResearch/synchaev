
import streamlit as st
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import chat1, chat2, mysql_agent_prompt_improved, environment_prompt_template, process_task_environment
from copy import deepcopy
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import re

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


# Function to add a message to the conversation
#def add_message(message):
#    st.session_state.messages.append(message)




# Modified chat_bubble function
def chat_bubble(conversation, index, participant, text):
    avatar = "🤖" if participant.lower() == "ai" else "🌍"

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
                    play_from_point(st, conversation, index, participant)
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
                        del st.session_state['environment_messages'][index:]
                        del st.session_state['agent_messages'][index+3:]
                    st.rerun()



def main():
    st.set_page_config(layout="wide")
    #st.markdown(bubble_style, unsafe_allow_html=True)
    st.title("Synchaev")
    # Create a chat conversation from chat1 and display it

    # Displaying the conversation
    col_agent, col_environment = st.columns([5, 5])

    # Agent conversation
    with col_agent:
        st.subheader('Agent')
        for index in range(len(st.session_state.agent_messages)):
            message = st.session_state.agent_messages[index]
            chat_bubble("agent", index, message.type, message.content)  
        if st.button('Add Agent Message'):
            agent_response = model.predict_messages(st.session_state.agent_messages)
            st.session_state['agent_messages'].append(agent_response)
            st.session_state['environment_messages'].append(HumanMessage(content=agent_response.content))

    # Environment conversation
    with col_environment:
        st.subheader('Environment')
        for index in range(len(st.session_state.environment_messages)):
            message = st.session_state.environment_messages[index]
            chat_bubble("environment", index, message.type, message.content) 
        if st.button('Add Environment Message'):
            st.session_state['environment_messages'].append('Environment message')
   
   #st.write("Edit Mode States:", st.session_state.edit_mode)


if __name__ == "__main__":
    main()
