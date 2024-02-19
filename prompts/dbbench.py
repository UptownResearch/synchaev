from langchain.schema import HumanMessage, AIMessage, SystemMessage

db_chat1 = [HumanMessage(content='I will ask you a question, then you should help me operate a MySQL database with SQL to answer the question.\nYou have to explain the problem and your solution to me and write down your thoughts.\nAfter thinking and explaining thoroughly, every round you can choose to operate or to answer.\nyour operation should be like this:\nAction: Operation\n```sql\nSELECT * FROM table WHERE condition;\n```\nYou MUST put SQL in markdown format without any other comments. Your SQL should be in one line.\nEvery time you can only execute one SQL statement. I will only execute the statement in the first SQL code block. Every time you write a SQL, I will execute it for you and give you the output.\nIf you are done operating, and you want to commit your final answer, then write down:\nAction: Answer\nFinal Answer: ["ANSWER1", "ANSWER2", ...]\nDO NOT write this pattern unless you are sure about your answer. I expect an accurate and correct answer.\nYour answer should be accurate. Your answer must be exactly the same as the correct answer.\nIf the question is about modifying the database, then after done operation, your answer field can be anything.\nIf your response cannot match any pattern I mentioned earlier, you will be judged as FAIL immediately.\nYour input will be raw MySQL response, you have to deal with it by yourself.', additional_kwargs={}, example=False),
 AIMessage(content='Ok.', additional_kwargs={}, example=False),
 HumanMessage(content="Query to find the total sales made by the employee 'Alejandra Mendoza'.. There are 2 tables involved in this task. The first table is named 'employees' with headers 'emp_id', 'first_name', 'last_name', 'email', 'phone_number'. The second table is named 'sales' with headers 'sale_id', 'emp_id', 'product_id', 'quantity', 'sale_date', 'total_price'. ", additional_kwargs={}, example=False),
 AIMessage(content="To find the total sales made by 'Alejandra Mendoza', we need to join the 'employees' table and the 'sales' table using the 'emp_id' field. This will allow us to find the sales entries associated with the given employee.\n\nFirst, we have to find out the 'emp_id' of 'Alejandra Mendoza'. Let's find his 'emp_id' in the 'employees' table.\n\nAction: Operation \n```sql\nSELECT emp_id FROM employees WHERE first_name='Alejandra' AND last_name='Mendoza'\n```", additional_kwargs={}, example=False),
 HumanMessage(content="```Output\n[(1,)]\n```", additional_kwargs={}, example=False),
 AIMessage(content="Alejandra Mendoza's employee ID (emp_id) is 1. \n\nNow, we will use this emp_id to find the total sales made by Alejandra Mendoza. We will sum the 'total_price' from the 'sales' table where 'emp_id' is 1. \n\nAction: Operation \n```sql\nSELECT SUM(total_price) FROM sales WHERE emp_id=1\n```", additional_kwargs={}, example=False),
 HumanMessage(content="```Output\n[(5000,)]\n```", additional_kwargs={}, example=False),
 AIMessage(content='Action: Answer\nFinal Answer: ["5000"]', additional_kwargs={}, example=False)]



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

Task and Database state:\nQuery to find the total sales made by the employee 'Alejandra Mendoza'. There are 2 tables involved in this task. The first table is named 'employees' with headers 'emp_id', 'first_name', 'last_name', 'email', 'phone_number'. The second table is named 'sales' with headers 'sale_id', 'emp_id', 'product_id', 'quantity', 'sale_date', 'total_price'.

SQL command:
```
SELECT emp_id FROM employees WHERE first_name='Alejandra' AND last_name='Mendoza';
```

Please ONLY respond in rawMySQL format (**with no extra formatting or commentary**) for a user of mysql-connector-python. Your output should STRICTLY be in ```Output\n<MySQL Output>\n```. For example, if the result is 59.555, the result would be presented as ```Output\n[('59.555',)]\n```. After responding, END your response.""", additional_kwargs={}, example=False),
 AIMessage(content="```Output\n[(1,)]\n```", additional_kwargs={}, example=False),
 HumanMessage(content='SELECT SUM(total_price) FROM sales WHERE emp_id=1;', additional_kwargs={}, example=False),
 AIMessage(content="```Output\n[(5000,)]\n```", additional_kwargs={}, example=False)
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
