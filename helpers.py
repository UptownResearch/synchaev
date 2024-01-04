from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
import re
from fastchat import FastChatAgent

# model = ChatOpenAI(model="gpt-4-0613")
# model.temperature = 0.8

model_name = 'Llama-2-7b-chat-hf'
controller_address = None
worker_address = "https://iv25t5kp7tzwju-8800.proxy.runpod.net"
temperature = 0.8
max_new_tokens = 512
top_p = 0


model = FastChatAgent(model_name, controller_address=controller_address, worker_address=worker_address, 
                         temperature=temperature , max_new_tokens=max_new_tokens)


environment_model = ChatOpenAI(model="gpt-4-0613")
environment_model.temperature = 0.8

class NoneMessage:
    def __init__(self, content=""):
        # Constructor for initializing the ChatContent class
        self.type = ""
        self.content = content
        self.is_placeholder = True

# Custom CSS for chat bubbles
bubble_style = """
<style>
.bubble {
    border-radius: 20px;
    padding: 10px;
    margin: 10px 0;
}

.bubble.human {
    background-color: #ADD8E6;
    text-align: left;
}

.bubble.ai {
    background-color: #90EE90;
    text-align: right;
}

.button-row {
    display: flex;
    gap: 5px;
    justify-content: flex-end;
}
</style>
"""


chat1 = [HumanMessage(content='I will ask you a question, then you should help me operate a MySQL database with SQL to answer the question. \nYou have to explain the problem and your solution to me and write down your thoughts. After thinking and explaining \nthoroughly, every round you can choose to operate or to answer. your operation should be like this: \nAction: Operation ```sql SELECT * FROM table WHERE condition; ``` You MUST put SQL in markdown format \nwithout any other comments. Your SQL should be in one line. Every time you can only execute one SQL statement. \nI will only execute the statement in the first SQL code block. Every time you write a SQL, I will execute it for you \nand give you the output. If the output is zero, or empty, you should always double check that you haven\'t made a mistake before submitting a final answer.\nYou can double check by removing limitations from your previous SQL statement until you get non-zero or non-empty results.\nIf you are done operating, and you want to commit your final answer, then write down: \nAction: Answer Final Answer: ["ANSWER1", "ANSWER2", ...] DO NOT write this pattern unless you are sure about your \nanswer. You must ALWAYS provide SQL or a Final Answer. I expect an accurate and correct answer. Your answer should be accurate. \nYour answer must be exactly the same as the correct answer. If the question is about modifying the database, then after you are done with operation, \nyour answer field can be anything. If your response cannot match any pattern I mentioned earlier, \nyou will be judged as FAIL immediately. Your input will be raw MySQL response, you have to deal with it by yourself.', additional_kwargs={}, example=False),
 AIMessage(content='Ok.', additional_kwargs={}, example=False),
 HumanMessage(content="Query to find the total sales made by the employee 'John Doe'.. There are 2 tables involved in this task. The first table is named 'employees' with headers 'emp_id', 'first_name', 'last_name', 'email', 'phone_number'. The second table is named 'sales' with headers 'sale_id', 'emp_id', 'product_id', 'quantity', 'sale_date', 'total_price'. ", additional_kwargs={}, example=False),
 AIMessage(content="To find the total sales made by 'John Doe', we need to join the 'employees' table and the 'sales' table using the 'emp_id' field. This will allow us to find the sales entries associated with the given employee.\n\nFirst, we have to find out the 'emp_id' of 'John Doe'. Let's find his 'emp_id' in the 'employees' table.\n\nAction: Operation \n```sql\nSELECT emp_id FROM employees WHERE first_name='John' AND last_name='Doe';\n```", additional_kwargs={}, example=False),
 HumanMessage(content='[(1,)]', additional_kwargs={}, example=False),
 AIMessage(content="John Doe's employee ID (emp_id) is 1. \n\nNow, we will use this emp_id to find the total sales made by John Doe. We will sum the 'total_price' from the 'sales' table where 'emp_id' is 1. \n\nAction: Operation \n```sql\nSELECT SUM(total_price) FROM sales WHERE emp_id=1;\n```", additional_kwargs={}, example=False),
 HumanMessage(content='[(24900,)]', additional_kwargs={}, example=False),
 AIMessage(content='Action: Answer\nFinal Answer: [24900]', additional_kwargs={}, example=False)]



chat2 = [HumanMessage(content="Pretend you are a MySQL database, responding to SQL statements from an agent. Provide realistic MySQL outputs for SELECT, INSERT, UPDATE, and DELETE operations, maintaining the state of the simulated database accordingly.  The user is expecting answers like those that would be received when using  mysql-connector-python. Reflect changes in subsequent outputs, and confirm operations with typical MySQL success messages. The initial state of the database is described below\n\nInitial Database state:\n There are 2 tables involved in this task. The first table is named 'employees' with headers 'emp_id', 'first_name', 'last_name', 'email', 'phone_number'. The second table is named 'sales' with headers 'sale_id', 'emp_id', 'product_id', 'quantity', 'sale_date', 'total_price'. \n\nFirst command:\nSELECT emp_id FROM employees WHERE first_name='John' AND last_name='Doe';\n\nThe user is working on the following task. The Database may include state that helps the user complete the task:\nQuery to find the total sales made by the employee 'John Doe'\n\nPlease only respond in rawMySQL format (with no extra formatting or commentary) for a user of  mysql-connector-python, for example, if the result is 59.555, the result would be presented as [('59.555',)]. After responding, end your response.\n", additional_kwargs={}, example=False),
 AIMessage(content='[(1,)]', additional_kwargs={}, example=False),
 HumanMessage(content='SELECT SUM(total_price) FROM sales WHERE emp_id=1;', additional_kwargs={}, example=False),
 AIMessage(content='[(24900,)]', additional_kwargs={}, example=False)
 ]


mysql_agent_prompt_improved = '''I will ask you a question, then you should help me operate a MySQL database with SQL to answer the question. 
You have to explain the problem and your solution to me and write down your thoughts. After thinking and explaining 
thoroughly, every round you can choose to operate or to answer. your operation should be like this: 
Action: Operation ```sql SELECT * FROM table WHERE condition; ``` You MUST put SQL in markdown format 
without any other comments. Your SQL should be in one line. Every time you can only execute one SQL statement. 
I will only execute the statement in the first SQL code block. Every time you write a SQL, I will execute it for you 
and give you the output. If the output is zero, or empty, you should always double check that you haven't made a mistake before submitting a final answer.
You can double check by removing limitations from your previous SQL statement until you get non-zero or non-empty results.
If you are done operating, and you want to commit your final answer, then write down: 
Action: Answer Final Answer: ["ANSWER1", "ANSWER2", ...] DO NOT write this pattern unless you are sure about your 
answer. You must ALWAYS provide SQL or a Final Answer. I expect an accurate and correct answer. Your answer should be accurate. 
Your answer must be exactly the same as the correct answer. If the question is about modifying the database, then after you are done with operation, 
your answer field can be anything. If your response cannot match any pattern I mentioned earlier, 
you will be judged as FAIL immediately. Your input will be raw MySQL response, you have to deal with it by yourself.'''


environment_prompt_template = '''Pretend you are a MySQL database, responding to SQL statements from an agent. Provide realistic MySQL outputs for SELECT, INSERT, UPDATE, and DELETE operations, maintaining the state of the simulated database accordingly.  The user is expecting answers like those that would be received when using  mysql-connector-python. Reflect changes in subsequent outputs, and confirm operations with typical MySQL success messages. The initial state of the database is described below

Initial Database state:
{}

First command:
{}

The user is working on the following task. The Database may include state that helps the user complete the task:
{}

Please only respond in rawMySQL format (with no extra formatting or commentary) for a user of  mysql-connector-python, for example, if the result is 59.555, the result would be presented as [('59.555',)]. After responding, end your response.
'''

def process_task_environment(data):
    return (data.split("..")[0], '\n'.join(data.split("..")[1:]))

def play_from_point(st, agent_model, environment_model, conversation, index, participant):
    print("\nplay_from_point\n\n")
    step = 0
    # first, delete conversation after current location
    if conversation == "agent": 
        # possible values of index = [1,3, 5...]
        delete_from = max(3, index)
        print(f" Deleting {st.session_state['agent_messages'][delete_from+1:]}\n\n")
        del st.session_state['agent_messages'][delete_from+1:]
        if index <= 3: 
            print(f" Deleting all environment messages.\n\n")
            st.session_state['environment_messages'] = []
        else:
            print(f" Deleting {st.session_state['environment_messages'][index - 2:]}\n\n")
            del st.session_state['environment_messages'][index - 2:]
    else:
        # possible values of index = [1, 3, ...]
        print(f" Deleting {st.session_state['environment_messages'][index - 2:]}\n\n")
        print(f" Deleting {st.session_state['agent_messages'][index:]}\n\n")
                
        del st.session_state['environment_messages'][index - 2:]
        del st.session_state['agent_messages'][index:]

        # replace last agent message
        message = st.session_state['environment_messages'][-1].content
        st.session_state['agent_messages'].append(HumanMessage(content =message))

    if conversation == "agent" and index == 1:
        step = 1
    if conversation == "agent" and index == 3:
        step = 2
    if conversation == "environment" and index == 4:
        step = 5
    if conversation == "agent" and index > 3:
        step = 4
    if conversation == "environment" and index >= 4:
        step = 5

    print(f"\nIndex: {index} Determined Step: {step}")

    if step < 3:
        if  st.session_state['agent_messages'][-1].type == "HumanMessage":
            agent_response = agent_model.predict_messages(st.session_state['agent_messages'])
            st.session_state['agent_messages'].append(agent_response)
            print(agent_response.content + "\n")
    if step < 4:
        first_response = st.session_state['agent_messages'][3].content
        first_sql_block = re.search(r"```sql(.*?)```", first_response, re.DOTALL)
        if first_sql_block:
            sql_code = first_sql_block.group(1).strip()
        else:
            sql_code = ""

        task_, environment_info = process_task_environment(st.session_state['agent_messages'][2].content)
        environment_prompt = environment_prompt_template.format(environment_info, sql_code, task_)
        st.session_state['environment_messages'] = [
            HumanMessage(content=environment_prompt)
        ]
        print(environment_prompt)
        environment_result = environment_model.predict_messages(st.session_state['environment_messages'])
        st.session_state['environment_messages'].append(environment_result)
        st.session_state['agent_messages'].append(HumanMessage(content=environment_result.content))
        print(environment_result.content + "\n")
    
    skip_once = False
    if step == 4:
        skip_once = True
        if st.session_state['environment_messages'][-1].type == "ai":
            sql_block = re.search(r"```sql(.*?)```", st.session_state['agent_messages'][-1].content, re.DOTALL)
            if sql_block:
                sql_code = sql_block.group(1).strip()
            else:
                sql_code = ""  
            st.session_state['environment_messages'].append(HumanMessage(content=sql_code))
            print(st.session_state['environment_messages'][-1])

    num_turns = 10 
    for i in range(num_turns):
        if not skip_once:
            agent_response = agent_model.predict_messages(st.session_state['agent_messages'])
            print(agent_response.content)
            first_sql_block = re.search(r"```sql(.*?)```", agent_response.content, re.DOTALL)
            if first_sql_block:
                sql_code = first_sql_block.group(1).strip()
            else:
                sql_code = ""
            st.session_state['agent_messages'].append(agent_response)
            if "Final Answer:" in agent_response.content:
                break
            st.session_state['environment_messages'].append(HumanMessage(content=sql_code))
        else:
            skip_once = False
        environment_result = environment_model.predict_messages(st.session_state['environment_messages'])
        st.session_state['environment_messages'].append(environment_result)
        print(environment_result.content)
        st.session_state['agent_messages'].append(HumanMessage(content=environment_result.content))



# DEPRECATED --- MARKED FOR DELETION
# Function to estimate the height of a chat bubble based on its content
def estimate_bubble_height(text):
    # This is a simplistic approach; you might need a more sophisticated method
    lines = text.count('\n') + 1
    height_per_line = 10  # adjust this based on your app's styling
    return lines * height_per_line + 10  # additional padding or fixed height

# DEPRECATED --- MARKED FOR DELETION
# Function to get the maximum length of both conversations
def max_conversation_length():
    return max(len(st.session_state.agent_messages), len(st.session_state.environment_messages))





# Modified chat_bubble function
def chat_bubble(st, conversation, index, participant, text, is_placeholder=False):
    avatar = ""
    if participant is not None:
        avatar = "🤖" if participant.lower() == "ai" else "🌍"
    if is_placeholder:
        avatar = "⚪️"
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
                    st.session_state.cc.update_agent_side(st.session_state.example_index, index, st.session_state.edited_text[conversation][index])
                else:
                    st.session_state.cc.update_environment_side(st.session_state.example_index, index, st.session_state.edited_text[conversation][index])
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
                        st.session_state.cc.replay_from_index(st.session_state.example_index, conversation, index)
                        st.rerun()
            with col3:    
                if participant.lower() == "ai":
                    if st.button('🔄', key=f'{conversation}_refresh_{index}'):
                        st.session_state.cc.refresh_at_index(st.session_state.example_index, conversation, index)
                        st.rerun()

            with col4:
                if not is_placeholder:
                    if st.button('✏️', key=f'{conversation}_edit_{index}'):
                        # Toggle edit mode
                        st.session_state.edit_mode[conversation][index] = not st.session_state.edit_mode[conversation].get(index, False)
                        st.rerun()
            with col5:
                if participant.lower() == "ai":
                    if st.button('🗑️',  key=f'{conversation}_delete_{index}'):
                        # Delete the message
                        st.session_state.cc.delete_at_index(st.session_state.example_index, conversation, index)
                        st.rerun()



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

