from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
import re
from fastchat import FastChatAgent

# model = ChatOpenAI(model="gpt-4-0613")
# model.temperature = 0.8

model_name = 'Llama-2-7b-chat-hf'
controller_address = None
worker_address = "https://qbckrkeybocx0v-8800.proxy.runpod.net"
temperature = 1.2
max_new_tokens = 512
top_p = 0.5


# model = FastChatAgent(model_name, controller_address=controller_address, worker_address=worker_address, 
#                          temperature=temperature , max_new_tokens=max_new_tokens, top_p=top_p)
model = ChatOpenAI(model="gpt-4-0613")
model.temperature = 0.8


environment_model = ChatOpenAI(model="gpt-4-0613")
environment_model.temperature = 0.0

creator_model = ChatOpenAI(model="gpt-4-0613")
creator_model.temperature = 0.8

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


# --------------------------DBBench Prompts-------------------------
db_chat1 = [HumanMessage(content='I will ask you a question, then you should help me operate a MySQL database with SQL to answer the question.\nYou have to explain the problem and your solution to me and write down your thoughts.\nAfter thinking and explaining thoroughly, every round you can choose to operate or to answer.\nyour operation should be like this:\nAction: Operation\n```sql\nSELECT * FROM table WHERE condition;\n```\nYou MUST put SQL in markdown format without any other comments. Your SQL should be in one line.\nEvery time you can only execute one SQL statement. I will only execute the statement in the first SQL code block. Every time you write a SQL, I will execute it for you and give you the output.\nIf you are done operating, and you want to commit your final answer, then write down:\nAction: Answer\nFinal Answer: ["ANSWER1", "ANSWER2", ...]\nDO NOT write this pattern unless you are sure about your answer. I expect an accurate and correct answer.\nYour answer should be accurate. Your answer must be exactly the same as the correct answer.\nIf the question is about modifying the database, then after done operation, your answer field can be anything.\nIf your response cannot match any pattern I mentioned earlier, you will be judged as FAIL immediately.\nYour input will be raw MySQL response, you have to deal with it by yourself.', additional_kwargs={}, example=False),
 AIMessage(content='Ok.', additional_kwargs={}, example=False),
 HumanMessage(content="Query to find the total sales made by the employee 'John Doe'.. There are 2 tables involved in this task. The first table is named 'employees' with headers 'emp_id', 'first_name', 'last_name', 'email', 'phone_number'. The second table is named 'sales' with headers 'sale_id', 'emp_id', 'product_id', 'quantity', 'sale_date', 'total_price'. ", additional_kwargs={}, example=False),
 AIMessage(content="To find the total sales made by 'John Doe', we need to join the 'employees' table and the 'sales' table using the 'emp_id' field. This will allow us to find the sales entries associated with the given employee.\n\nFirst, we have to find out the 'emp_id' of 'John Doe'. Let's find his 'emp_id' in the 'employees' table.\n\nAction: Operation \n```sql\nSELECT emp_id FROM employees WHERE first_name='John' AND last_name='Doe';\n```", additional_kwargs={}, example=False),
 HumanMessage(content="```Output\n[(1,)]\n```", additional_kwargs={}, example=False),
 AIMessage(content="John Doe's employee ID (emp_id) is 1. \n\nNow, we will use this emp_id to find the total sales made by John Doe. We will sum the 'total_price' from the 'sales' table where 'emp_id' is 1. \n\nAction: Operation \n```sql\nSELECT SUM(total_price) FROM sales WHERE emp_id=1;\n```", additional_kwargs={}, example=False),
 HumanMessage(content="```Output\n[(24900,)]\n```", additional_kwargs={}, example=False),
 AIMessage(content='Action: Answer\nFinal Answer: ["24900"]', additional_kwargs={}, example=False)]



db_chat2 = [HumanMessage(content="""Pretend you are a MySQL database, responding to SQL statements from an agent. Provide realistic MySQL outputs for SELECT, INSERT, UPDATE, and DELETE operations, maintaining the state of the simulated database accordingly. The user is expecting answers like those that would be received when using  mysql-connector-python. Reflect changes in subsequent outputs, and confirm operations with typical MySQL success messages. The initial state of the database is described below:

Tables: 
```Table
employees

| emp_id | first_name | last_name | email                | phone_number |
|--------|------------|-----------|----------------------|--------------|
| 1      | Alejandra  | Mendoza   | a.mendoza@gmail.com  | 5543127890   |
| 2      | Kofi       | Mensah    | k.mensah@hotmail.com | 23324356789  |
| 3      | Mei        | Li        | m.li@yahoo.com       | 86123456789  |
| 4      | Svetlana   | Ivanova   | s.ivanova@aol.com    | 74951234567  |
| 5      | Ahmed      | Hussein   | a.hussein@gmail.com  | 20123456789  |
```

```Table
sales

| sale_id | emp_id | product_id | quantity | sale_date  | total_price |
|---------|--------|------------|----------|------------|-------------|
| 1001    | 1      | 2001       | 50       | 2020-01-01 | 5000        |
| 1002    | 2      | 2002       | 30       | 2020-02-01 | 3000        |
| 1003    | 3      | 2003       | 20       | 2020-03-01 | 2000        |
| 1004    | 4      | 2004       | 10       | 2020-04-01 | 1000        |
| 1005    | 5      | 2005       | 5        | 2020-05-01 | 500         |
```

Task and Database state:\nQuery to find the total sales made by the employee 'John Doe'. There are 2 tables involved in this task. The first table is named 'employees' with headers 'emp_id', 'first_name', 'last_name', 'email', 'phone_number'. The second table is named 'sales' with headers 'sale_id', 'emp_id', 'product_id', 'quantity', 'sale_date', 'total_price'.

SQL command:
```
SELECT emp_id FROM employees WHERE first_name='John' AND last_name='Doe';
```

Please ONLY respond in rawMySQL format (**with no extra formatting or commentary**) for a user of mysql-connector-python. Your output should STRICTLY be in ```Output\n<MySQL Output>\n```. For example, if the result is 59.555, the result would be presented as ```Output\n[('59.555',)]\n```. After responding, END your response.""", additional_kwargs={}, example=False),
 AIMessage(content="```Output\n[(1,)]\n```", additional_kwargs={}, example=False),
 HumanMessage(content='SELECT SUM(total_price) FROM sales WHERE emp_id=1;', additional_kwargs={}, example=False),
 AIMessage(content="```Output\n[(24900,)]\n```", additional_kwargs={}, example=False)
 ]

db_chat3 = [SystemMessage(content="Create fake SQL tables for the given query (DO NOT produce the SQL code but just create fake tables which is related to the task and the description). You should not write the commands to create the tables but just write down the table contents. The tables you create should look like real ones and be diverse in the contents you imagine. DO NOT use common names, addresses, etc, but make it diverse and new. For easy parsing of your outputs make sure to put the tables as ```Table\n<THE TABLE YOU IMAGINE>\n```.", additional_kwargs={}, example=False),
HumanMessage(content=f"How many French drivers who obtain the laptime less than 01:00.00?\nThere are 2 tables involved with this task. The name of the 1st table is drivers, and the headers of this table are driverId,driverRef,number,code,forename,surname,dob,nationality,url. The name of the 2nd table is lapTimes, and the headers of this table are raceId,driverId,lap,position,time,milliseconds.", additional_kwargs={}, example=False),
 AIMessage(content='''```Table
drivers
| driverId | driverRef | number | code | forename  | surname  | dob        | nationality | url                                |
|----------|-----------|--------|------|-----------|----------|------------|-------------|------------------------------------|
| 1        | ref1      | 44     | LH   | Lewis     | Hamilton | 1985-01-07 | British     | http://www.lewishamilton.com       |
| 2        | ref2      | 33     | MV   | Max       | Verstappen | 1997-09-30 | Dutch      | http://www.maxverstappen.com       |
| 3        | ref3      | 16     | CL   | Charles   | Leclerc  | 1997-10-16 | Monegasque  | http://www.charlesleclerc.com      |
| 4        | ref4      | 77     | VB   | Valtteri  | Bottas   | 1989-08-28 | Finnish     | http://www.valtteribottas.com      |
| 5        | ref5      | 5      | SV   | Sebastian | Vettel   | 1987-07-03 | German      | http://www.sebastianvettel.com     |
```

```Table
lapTimes
| raceId | driverId | lap | position | time  | milliseconds |
|--------|----------|-----|----------|-------|--------------|
| 1      | 1        | 1   | 1        | 1:34  | 94000        |
| 1      | 2        | 1   | 2        | 1:35  | 95000        |
| 1      | 3        | 1   | 3        | 1:36  | 96000        |
| 1      | 4        | 1   | 4        | 1:37  | 97000        |
| 2      | 1        | 2   | 1        | 1:33  | 93000        |
| 2      | 2        | 2   | 2        | 1:34  | 94000        |
| 2      | 3        | 2   | 3        | 1:35  | 95000        |
| 2      | 4        | 2   | 4        | 1:36  | 96000        |
```''', additional_kwargs={}, example=False),
 ] 

db_agent_prompt_improved = '''I will ask you a question, then you should help me operate a MySQL database with SQL to answer the question. 
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

db_environment_prompt_template = '''Here is a new database and task.
Tables:
{}

Task and Database state:
{}

SQL command:
```
{}
```

Please ONLY respond in rawMySQL format (**with no extra formatting or commentary**) for a user of mysql-connector-python. Your output should STRICTLY be in ```Output\n<MySQL Output>\n```. For example, if the result is 59.555, the result would be presented as ```Output\n[('59.555',)]\n```. After responding, END your response.
'''
# db_environment_prompt_template = '''Pretend you are a MySQL database, responding to SQL statements from an agent. Provide realistic MySQL outputs for SELECT, INSERT, UPDATE, and DELETE operations, maintaining the state of the simulated database accordingly. The user is expecting answers like those that would be received when using  mysql-connector-python. Reflect changes in subsequent outputs, and confirm operations with typical MySQL success messages. The initial state of the database is described below

# Tables:
# {}

# Task and Database state:
# {}

# SQL command:
# ```
# {}
# ```

# Please ONLY respond in rawMySQL format (**with no extra formatting or commentary**) for a user of mysql-connector-python. Your output should STRICTLY be in ```Output\n<MySQL Output>\n```. For example, if the result is 59.555, the result would be presented as ```Output\n[('59.555',)]\n```. After responding, END your response.
# '''


# --------------------------OS-Interaction Prompts-------------------------
os_chat1 = [HumanMessage(content='You are an assistant that will act like a person, I\'will play the role of linux(ubuntu) operating system. Your goal is to implement the operations required by me or answer to the question proposed by me. For each of your turn, you should first think what you should do, and then take exact one of the three actions: "bash", "finish" or "answer". \n\n1. If you think you should execute some bash code, take bash action, and you should print like this:\n\nThink: put your thought here.\n\nAct: bash\n\n```bash\n# put your bash code here\n```\n\n2. If you think you have finished the task, take finish action, and you should print like this:\n\nThink: put your thought here.\n\nAct: finish\n\n3. If you think you have got the answer to the question, take answer action, and you should print like this:\n\nThink: put your thought here.\n\nAct: answer(Your answer to the question should be put in this pair of parentheses)\n\nIf the output is too long, I will truncate it. The truncated output is not complete. You have to deal with the truncating problem by yourself. Attention, your bash code should not contain any input operation. Once again, you should take only exact one of the three actions in each turn.\n\nNow, my problem is:\n\ntell me how many files are in the directory "/etc"?bash:`', additional_kwargs={}, example=False),
AIMessage(content='Think: To count the files in /etc, I need to print all the files in it.\n\nAct: bash\n\n```bash\nls /etc\n```', additional_kwargs={}, example=False),
HumanMessage(content='The output of the OS:\n```Output\ncpi cron.hourly fuse.conf iproute2 lvm networkd-dispatcher protocols selinux tmpfiles.d [truncated because the output is too long]\n```', additional_kwargs={}, example=False),
AIMessage(content='Think: The output has been truncated because it is too long, so I need to count files by script directly.\n\nAct: bash\n\n```bash\nls -1 /etc | wc -l\n```', additional_kwargs={}, example=False),
HumanMessage(content='The output of the OS:\n```Output\n12\n```', additional_kwargs={}, example=False),
AIMessage(content='Think: Now I get the answer, it is 12.\n\nAct: answer(12)', additional_kwargs={}, example=False),]

os_chat2 = [HumanMessage(content="""Please take on the role of a linux(ubuntu) environment. I will send **bash commands** which the user takes in the process to solve a given **task**. You will respond with the output that is as close to the output of the linux environment as possible.
Limit the response to around 250 characters. Truncate the output if it overflows the limit by the message "[truncated because the output is too long]".  Do not repeat the command provided. 
Before performing the task a set of bash commands are run which initializes the state of the OS.
Let's start!

Task: tell me how many files are in the directory "/etc"?
Initialization command:
```bash
mkdir -p ./etc
cd ./etc
sudo touch cpi cron.hourly fuse.conf iproute2 lvm networkd-dispatcher protocols selinux tmpfiles.d notes.txt selenium_img.png vocal.py
```
Bash command: 
```bash
ls /etc
```""", additional_kwargs={}, example=False),
AIMessage(content='The output of the OS:\n```Output\ncpi cron.hourly fuse.conf iproute2 lvm networkd-dispatcher protocols selinux tmpfiles.d [truncated because the output is too long]\n```', additional_kwargs={}, example=False),
HumanMessage(content='''Bash Command:
```bash
ls -1 /etc | wc -l
```''', additional_kwargs={}, example=False),
AIMessage(content='The output of the OS:\n```Output\n12\n```', additional_kwargs={}, example=False)]

os_chat3 = [SystemMessage(content='''Given is a task you have to perform in a Linux OS environment. You have to generate a set of bash commands which can initialize the environment to a necessary state needed to perform the given task. The initialization commands will create a dummy state of the environment which should be as close to the reality.
For example, if the task is to find the number of files with extension .txt in the home directory, the initialization command should initialize some dummy files with .txt extensions. 
When there is no initialization command required before a task, just output an empty string in place of the bash command.''', additional_kwargs={}, example=False),
HumanMessage(content=f"Task: Recursively Find how many files have the extension .tep", additional_kwargs={}, example=False),
 AIMessage(content='''Initialization command: 
```bash
echo 123>/root/.tmp\necho 123>/root/.tmp2\necho 123>/root/1.tep\necho 123>/root/.tep\necho 123>/root/.u\necho 123>/root/.k
```''', additional_kwargs={}, example=False),
HumanMessage(content=f"Task: tell me how many files are in the directory '/etc'?", additional_kwargs={}, example=False),
 AIMessage(content='''Initialization command: 
```bash
sudo touch /etc/example1 /etc/example2 /etc/example3
```''', additional_kwargs={}, example=False),
HumanMessage(content=f"Task: Tell me the number of CPUs.", additional_kwargs={}, example=False),
 AIMessage(content='''No file and directory creation is required for this task because CPUs are a part of system hardware, they don't exist as files. So the initialization command will be an empty string.

Initialization command: 
```bash
```''', additional_kwargs={}, example=False),
 ] 

os_agent_prompt_improved = '''You are an assistant that will act like a person, I'will play the role of linux(ubuntu) operating system. Your goal is to implement the operations required by me or answer to the question proposed by me.
For each of your turn, you should first think what you should do, and then take exact one of the three actions: "bash", "finish" or "answer".

1. If you think you should execute some bash code, take bash action, and you should print like this:

Think: put your thought here.
Act: bash
```bash
# put your bash code here
```

2. If you think you have finished the task, take finish action, and you should print like this:

Think: put your thought here.
Act: finish

3. If you think you have got the answer to the question, take answer action, and you should print like this:

Think: put your thought here.
Act: answer(Your answer to the question should be put in this pair of parentheses)

If the output is too long, I will truncate it. The truncated output is not complete. You have to deal with the truncating problem by yourself. Attention, your bash code should not contain any input operation. Once again, you should take only exact one of the three actions in each turn.

Now my problem is:
{}'''

os_environment_prompt_template = """Task: {}
Initialization command:
```bash
{}
```
Bash command:
```bash
{}
```
"""


def read_pickle(file):
    import pickle
    with open(file, "rb") as file:
        data = pickle.load(file)
    return data

def save_json(data, file):
    import json
    with open(file, "w") as file:
        json.dump(data, file)

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
        environment_prompt = db_environment_prompt_template.format(environment_info, sql_code, task_)
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

