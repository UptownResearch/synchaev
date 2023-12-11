
import streamlit as st
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import chat1, chat2
from copy import deepcopy
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv() 
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

model = ChatOpenAI(model="gpt-4-0613")
model.temperature = 0.8

# Initialize a session state to store the conversation
if 'agent_messages' not in st.session_state:
    st.session_state.agent_messages = deepcopy(chat1)
# Initialize a session state to store the conversation
if 'environment_messages' not in st.session_state:
    st.session_state.environment_messages = deepcopy(chat2)

# Function to add a message to the conversation
#def add_message(message):
#    st.session_state.messages.append(message)

# Function to display a chat bubble with buttons below
def chat_bubble(conversation, index, participant, text):
    avatar = "🤖" if participant.lower() == "ai" else "🌍"
    
    with st.chat_message(name=participant, avatar=avatar):
        st.write(text)
        
        with st.container():
            # Display the buttons in a row below the bubble
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            with col1:
                pass
            with col2:
                if st.button('🔄', key=f'{conversation}_refresh_{index}'):
                    # Refresh logic
                    pass
            with col3:
                if st.button('✏️', key=f'{conversation}_edit_{index}'):
                    # Edit logic
                    pass
            with col4:
                if st.button('🗑️',  key=f'{conversation}_delete_{index}'):
                    # Delete the message
                    if conversation == 'agent':
                        del st.session_state['agent_messages'][index:]
                    else:
                        del st.session_state['environment_messages'][index:]
                    st.experimental_rerun()

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



    
if __name__ == "__main__":
    main()
