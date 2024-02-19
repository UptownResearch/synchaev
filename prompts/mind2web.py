from langchain.schema import HumanMessage, AIMessage, SystemMessage

m2w_chat1 = [HumanMessage(content="""'''
<html> <div> <div> <input id=0 text search for books by keyword searchterm /> <input search find book /> <button submit search> </button> </div> <a id=1> Bestsellers </a> <div> <ul> <a id=2> Complementary Medicine </a> <a id=3> Other Branches Of Medicine </a> </ul> <a id=4> <div> Diseases & Disorders </div> </a> </div> </div> </html>
'''

Based on the HTML webpage above, try to complete the following task:
Task: Find the latest medical audiobook on complementary medicine for under 20 dollars and add the top book to the cart.
Previous actions:
[link]  Shop by category∨ -> HOVER
[link]  Medical -> CLICK
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <input id=0 text search for books by keyword searchterm />
C. <a id=1> Bestsellers </a>
D. <a id=2> Complementary Medicine </a>
E. <a id=3> Other Branches Of Medicine </a>
F. <a id=4> <div> Diseases & Disorders </div> </a>""", additional_kwargs={}, example=False),
AIMessage(content="""Thought: The previous actions have already navigated to the desired information about baggage allowance for business class. No further action is required.
Answer: A. None of the above""", additional_kwargs={}, example=False)]

m2w_chat2 = [HumanMessage(content="""'''
<html> <div> <div> <input id=0 text search for books by keyword searchterm /> <input search find book /> <button submit search> </button> </div> <a id=1> Bestsellers </a> <div> <ul> <a id=2> Complementary Medicine </a> <a id=3> Other Branches Of Medicine </a> </ul> <a id=4> <div> Diseases & Disorders </div> </a> </div> </div> </html>
'''

Based on the HTML webpage above, try to complete the following task:
Task: Find the latest medical audiobook on complementary medicine for under 20 dollars and add the top book to the cart.
Previous actions:
[link]  Shop by category∨ -> HOVER
[link]  Medical -> CLICK
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <input id=0 text search for books by keyword searchterm />
C. <a id=1> Bestsellers </a>
D. <a id=2> Complementary Medicine </a>
E. <a id=3> Other Branches Of Medicine </a>
F. <a id=4> <div> Diseases & Disorders </div> </a>""", additional_kwargs={}, example=False)]

m2w_chat3 = [SystemMessage(content="""Given a task an agent has to perform in a web browser. You have to initialise the state of the browser before the agent starts its actions. For intitialisation you have to create a web page necessary for the task. You should only use HTML codes.""", additional_kwargs={}, example=False),
            HumanMessage(content="""Task: Find the latest medical audiobook on complementary medicine for under 20 dollars and add the top book to the cart.
Previous actions:
[link]  Shop by category∨ -> HOVER
[link]  Medical -> CLICK
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <input id=0 text search for books by keyword searchterm />
C. <a id=1> Bestsellers </a>
D. <a id=2> Complementary Medicine </a>
E. <a id=3> Other Branches Of Medicine </a>
F. <a id=4> <div> Diseases & Disorders </div> </a>""", additional_kwargs={}, example=False),
AIMessage(content="""'''
<html> <div> <div> <input id=0 text search for books by keyword searchterm /> <input search find book /> <button submit search> </button> </div> <a id=1> Bestsellers </a> <div> <ul> <a id=2> Complementary Medicine </a> <a id=3> Other Branches Of Medicine </a> </ul> <a id=4> <div> Diseases & Disorders </div> </a> </div> </div> </html>
'''""", additional_kwargs={}, example=False),
HumanMessage(content="""Task: Get a price quote for new Kia Carnival for 11101.
Previous actions:
[link]  Cars for Sale -> HOVER
[link]  Free Dealer Price Quote -> CLICK
[select]  Make -> SELECT: Kia
[select]  Model -> SELECT: Carnival
[textbox]  ZIP -> TYPE: 11101
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <select id=0 make> <option> Make </option> <option 2> Acura </option>
C. <select id=1 model> <option> Model </option> <option 40278 true> Carnival
D. <select id=2 style/trim> <option> Style/Trim </option> <option 367228 true> EX
E. <input id=3 zipinput 11101 />
F. <button id=4 submit step1button> <span> Find Dealers </span> </button>""", additional_kwargs={}, example=False),
AIMessage(content="""'''
<html> <iframe new car price quote> <div> <div> <select id=0 make> <option> Make </option> <option 2> Acura </option> <option 3> Alfa Romeo </option> <option 4> Audi </option> <option 5> BMW </option> <option 7> Buick </option> <option 8> Cadillac </option> <option 9> Chevrolet </option> <option 10> Chrysler </option> <option 13> Dodge </option> <option 430> FIAT </option> <option 840> Fisker </option> <option 15> Ford </option> <option 897> Genesis </option> <option 16> GMC </option> <option 18> Honda </option> <option 20> Hyundai </option> <option 21> INFINITI </option> <option 23> Jaguar </option> <option 24> Jeep </option> <option 25 true> Kia </option> <option 26> Land Rover </option> <option 27> Lexus </option> <option 28> Lincoln </option> <option 917> Lucid </option> </select> <label> Make </label> </div> <div> <select id=1 model> <option> Model </option> <option 40278 true> Carnival </option> <option 40295> EV6 </option> <option 19588> Forte </option> <option 40265> K5 </option> <option 37482> Niro </option> <option 40216> Niro EV </option> <option 39121> Niro Plug-in Hybrid </option> <option 166> Rio </option> <option 40232> Seltos </option> <option 174> Sorento </option> <option 40292> Sorento Hybrid </option> <option 40336> Sorento Plug-in Hybrid </option> <option 18780> Soul </option> <option 171> Sportage </option> <option 40352> Sportage Hybrid </option> <option 40368> Sportage Plug-in Hybrid </option> <option 38760> Stinger </option> <option 40026> Telluride </option> </select> <label> Model </label> </div> <div> <select id=2 style/trim> <option> Style/Trim </option> <option 367228 true> EX </option> <option 364348> LX </option> <option 367239> LX w/Seat Pkg </option> <option 367243> SX </option> <option 367234> SX Prestige </option> </select> <label> Style/Trim </label> </div> <label> <input id=3 zipinput 11101 /> <div zipinput 11101> ZIP </div> </label> <button id=4 submit step1button> <span> Find Dealers </span> </button> </div> </iframe> </html>
'''""", additional_kwargs={}, example=False),
HumanMessage(content="""Task: Check the balance for a gift card with the number 1000000000000000 and pin 1222
Previous actions:
None
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <a id=0 visit the gift cards page> Gift Cards </a>
C. <a id=1> Gift Cards </a>""", additional_kwargs={}, example=False),
AIMessage(content="""'''
<html> <div> <header banner> <ul menu> <li menuitem> <a id=0 visit the gift cards page> Gift Cards </a> </li> </ul> </header> <footer contentinfo> <ul navigation> <a id=1> Gift Cards </a> </ul> </footer> </div> </html>
'''""", additional_kwargs={}, example=False)]

m2w_agent_prompt_improved = [HumanMessage(content="", additional_kwargs={}, example=False)]

m2w_environment_prompt_template = [HumanMessage(content="", additional_kwargs={}, example=False)]
