from langchain.schema import HumanMessage, AIMessage, SystemMessage

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
 AIMessage(content='[(24900,)]', additional_kwargs={}, example=False),
 HumanMessage(content='', additional_kwargs={}, example=False)]


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