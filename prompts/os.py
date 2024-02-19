from langchain.schema import HumanMessage, AIMessage, SystemMessage

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
