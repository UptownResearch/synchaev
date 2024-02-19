from langchain.schema import HumanMessage, AIMessage, SystemMessage

alf_chat1 = [HumanMessage(content='Interact with a household to solve a task. Imagine you are an intelligent agent in a household environment and your target is to perform actions to complete the task goal. At the beginning of your interactions, you will be given the detailed description of the current environment and your goal to accomplish. For each of your turn, you will be given a list of actions which you can choose one to perform in this turn. You should choose from two actions: "THOUGHT" or "ACTION". If you choose "THOUGHT", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format:"THOUGHT: your thoughts.\n ACTION: your next action\n"; If you choose "ACTION", you should directly output the action in this turn. Your output must strictly follow this format:"ACTION: your next action\n". After your each turn, the environment will give you immediate feedback based on which you plan your next few steps. if the envrionment output "Nothing happened", that means the previous action is invalid and you should try more options.\n Reminder: \n1. the action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal. \n2. Think when necessary, try to act directly more in the process.', additional_kwargs={}, example=False),
AIMessage(content="OK. I'll follow your instructions and try my best to solve the task.", additional_kwargs={}, example=False),
HumanMessage(content="Here is your task. You are in the middle of a room. Looking quickly around you, you see a bed 1, a diningtable 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a sidetable 2, and a sidetable 1. Your task is to: put a cd in sidetable.", additional_kwargs={}, example=False),
AIMessage(content="THOUGHT: The task is to put a cd in sidetable. First I need to find a cd. Drawers are the most probable place to find a cd. I'll start my search from drawer 1. ACTION: go to drawer 1", additional_kwargs={}, example=False),
HumanMessage(content="The drawer 1 is closed.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: open drawer 1", additional_kwargs={}, example=False),
HumanMessage(content="You open the drawer 1. The drawer 1 is open. In it, you see nothing.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: go to drawer 2", additional_kwargs={}, example=False),
HumanMessage(content="The drawer 2 is closed.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: open drawer 2", additional_kwargs={}, example=False),
HumanMessage(content="You open the drawer 2. The drawer 2 is open. In it, you see nothing.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: go to drawer 3", additional_kwargs={}, example=False),
HumanMessage(content="On the drawer 3, you see a keychain 1.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: go to drawer 4", additional_kwargs={}, example=False),
HumanMessage(content="On the drawer 4, you see a creditcard 1, and a keychain 2.", additional_kwargs={}, example=False),
AIMessage(content="THOUGHT: I've examined all drawers and couldn't find a CD. I need to look for other places. I'll check the diningtable next. ACTION: go to diningtable 1", additional_kwargs={}, example=False),
HumanMessage(content="On the diningtable 1, you see a cd 1, a cellphone 2, a creditcard 3, a creditcard 2, a keychain 3, a mug 2, a pen 2, a pen 1, a pencil 2, and a pencil 1.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: take cd 1 from diningtable 1", additional_kwargs={}, example=False),
HumanMessage(content="You pick up the cd 1 from the diningtable 1.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: go to sidetable 1", additional_kwargs={}, example=False),
HumanMessage(content="On the sidetable 1, you see a mug 1.", additional_kwargs={}, example=False),
AIMessage(content="ACTION: put cd 1 in/on sidetable 1", additional_kwargs={}, example=False),
HumanMessage(content='success("the agent has accomplished the task which was to put a cd in sidetable")', additional_kwargs={}, example=False),
]

alf_chat2 = [HumanMessage(content="""Your Goal is to simulate a household environment that an agent is acting in. For each turn, you will receive an action chosen by the agent. You must then respond as the environment according to the previous state of the environment. Along with the environment's response you should also generate the updated state of the environment. If the agent has accomplished the task, YOU MUST call the success function: "success("[why task was successful]")".
Below is the task the agent has been given along with the initial state of the environment.

Initial State:
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Task: You are in the middle of a room. Looking quickly around you, you see a bed 1, a diningtable 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a sidetable 2, and a sidetable 1. Your task is to: put a cd in sidetable.

Agent's First Action: THOUGHT: The task is to put a cd in sidetable. First I need to find a cd. Drawers are the most probable place to find a cd. I'll start my search from drawer 1. ACTION: go to drawer 1""", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: The drawer 1 is closed.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: open drawer 1", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: You open the drawer 1. The drawer 1 is open. In it, you see nothing.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: go to drawer 2", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: The drawer 2 is closed.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: open drawer 2", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: You open the drawer 2. The drawer 2 is open. In it, you see nothing.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: go to drawer 3", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: On the drawer 3, you see a keychain 1.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: go to drawer 4", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: On the drawer 4, you see a creditcard 1, and a keychain 2.""", additional_kwargs={}, example=False),
HumanMessage(content="THOUGHT: I've examined all drawers and couldn't find a CD. I need to look for other places. I'll check the diningtable next. ACTION: go to diningtable 1", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: On the diningtable 1, you see a cd 1, a cellphone 2, a creditcard 3, a creditcard 2, a keychain 3, a mug 2, a pen 2, a pen 1, a pencil 2, and a pencil 1.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: take cd 1 from diningtable 1", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: You pick up the cd 1 from the diningtable 1.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: go to sidetable 1", additional_kwargs={}, example=False),
AIMessage(content="""State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: On the sidetable 1, you see a mug 1.""", additional_kwargs={}, example=False),
HumanMessage(content="ACTION: put cd 1 in/on sidetable 1", additional_kwargs={}, example=False),
AIMessage(content='''State: 
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1", "cd 1"],
    "sidetable 2": ["alarmclock 1"]
}

Output: success("the agent has accomplished the task which was to put a cd in sidetable")''', additional_kwargs={}, example=False)]

alf_chat3 = [SystemMessage(content='''Given a task an agent has to perform in a household environment. You have to initialize the state of the house before the agent starts its actions. 
The initialization will consists of mapping each item present in the task description to the items present in its vicinity. The mapping should be a JSON for easy parsing. For example, when the agent opens drawer 1 it sees pen2.''', additional_kwargs={}, example=False),
HumanMessage(content=f"Task: You are in the middle of a room. Looking quickly around you, you see a bed 1, a diningtable 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a sidetable 2, and a sidetable 1. Your task is to: put a cd in sidetable.", additional_kwargs={}, example=False),
AIMessage(content='''Initial State:
{
    "bed 1": ["book 1", "cellphone 1", "laptop 1", "pillow 2", "pillow 1"],
    "diningtable 1": ["cd 1", "cellphone 2", "creditcard 3", "creditcard 2", "keychain 3", "mug 2", "pen 2", "pen 1", "pencil 2", "pencil 1"],
    "drawer 1": ["nothing"],
    "drawer 2": ["nothing"],
    "drawer 3": ["keychain 1"],
    "drawer 4": ["creditcard 1", "keychain 2"],
    "garbagecan 1": ["nothing"],
    "sidetable 1": ["mug 1"],
    "sidetable 2": ["alarmclock 1"]
}''', additional_kwargs={}, example=False),
] 

alf_agent_prompt_improved = '''Interact with a household to solve a task. Imagine you are an intelligent agent in a household environment and your target is to perform actions to complete the task goal. At the beginning of your interactions, you will be given the detailed description of the current environment and your goal to accomplish. For each of your turn, you will be given a list of actions which you can choose one to perform in this turn. You should choose from two actions: "THOUGHT" or "ACTION". If you choose "THOUGHT", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format:"THOUGHT: your thoughts.\n ACTION: your next action\n"; If you choose "ACTION", you should directly output the action in this turn. Your output must strictly follow this format:"ACTION: your next action\n". After your each turn, the environment will give you immediate feedback based on which you plan your next few steps. if the envrionment output "Nothing happened", that means the previous action is invalid and you should try more options.\n Reminder: \n1. the action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal. \n2. Think when necessary, try to act directly more in the process.s'''

alf_environment_prompt_template = """Now lets start a new task in a new environment.
Initial State:
{}

Task: 
{}

Agent's First Action:
{}"""
