# Instructions To Run

```
python main.py
```
1
• • • • • • • • •
You will perform a white-box testing exercise on an implementation of a board game Money- Poly. This program manages players, money, property purchases, rent payments, and other core game mechanics. There may be logical issues in the code, so your task is to analyze, test, and improve it using white-box testing techniques.
1.1 Control Flow Graph
Create a Control Flow Graph for the program and attach it in the report.
Requirements:
• Draw the graph by hand.
• Each node should represent a single statement or a block of related statements. • Arrows should clearly indicate the flow of control.
• All nodes must be labeled clearly.
• Submit a clear image of the diagram as part of your report.
1
1.2 Code Quality Analysis
Use pylint to analyze the codebase. Make sure to iteratively fix the code as per the warnings and suggestions. Document all the changes in the report.
Save each iteration as a commit in the format “Iteration #: <What You Changed>”
1.3 White Box Test Cases
Design white-box test cases based on the structure of the code. Your tests must cover: • All branches (every decision path)
• Key variable states that could affect program behavior
• Relevant edge cases (e.g. zero values, large inputs, unexpected player actions)
In the report, explain in simple words why each test case is needed, along with all the errors or logical issues found by the test.
Correct the code for each error and save it as a commit in the format “Error #: <What You Changed>”