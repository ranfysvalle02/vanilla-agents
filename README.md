## Building an Advanced AI Agent with MongoDB as Memory

![AI Agent Overview](https://upload.wikimedia.org/wikipedia/commons/a/aa/AI_Agent_Overview.png)

Crafting a generative AI *agent* doesn't require a mountain of complex libraries. With just a few well-placed lines of code, you can build a custom AI agent that can implement custom processes/workflows. This guide will equip you with the building blocks to forge your very own generative AI agent from scratch, giving you the freedom to experiment and innovate.

## Understanding Agent Abstraction

Agent Abstraction is a design pattern that allows us to automate complex workflows. It involves the creation of an 'Agent' that can execute a 'Process'. A Process is a series of 'Tasks', and each Task can utilize a set of 'Tools'. 

### Breaking Down the Process: Tasks and Tools

A process is essentially a recipe for automation. It's a series of steps, each focusing on a specific action. These steps are called tasks. 

Let's take a real-world example. Imagine a process for automatically generating social media posts from blog articles. One task could be summarizing the article, another converting the summary to an engaging format, and a final one might be posting it to your social media channels.

Each task can leverage a set of tools to complete its job.  In our social media example, tools might include a summarization engine, a text formatting script, and a social media posting API.

### Sequential vs. Parallel Execution: A Closer Look

The execution strategy of tasks is a crucial aspect of workflow automation. 

The agent can execute tasks in two primary ways: Sequentially and in Parallel. 

* **Sequential Execution:** This approach is akin to following a recipe. Each step (or task) must be completed in a specific order before proceeding to the next. For instance, in a content creation workflow, the agent might first summarize an article, then format the summary into a social media-friendly text, and finally, post it on the designated platform. Each task relies on the output of the previous one, creating a chain of dependencies. 

* **Parallel Execution:** This strategy is comparable to prepping ingredients for a meal. Several steps can occur simultaneously, enhancing efficiency. The agent can employ parallel execution for tasks that are independent, i.e., their outputs don't influence each other. For example, the agent could summarize an article while concurrently sending a text notification about the start of the process. Both tasks are independent, allowing them to run side-by-side without waiting for the other to complete.

Choosing between sequential and parallel execution depends on the nature of the tasks and their interdependencies. While parallel execution can speed up the process, it requires careful management to ensure that all tasks are completed correctly. Conversely, sequential execution might be slower but offers a straightforward, step-by-step progression that's easier to manage and debug.

**Caveats to Consider:**

* **Critical Tasks:** Some tasks might be essential for the entire workflow to function properly. The agent can be programmed to handle these critical tasks with priority and halt the process if they fail.
* **Tool Usage Limits:**  Sometimes, using a tool too frequently might have limitations (e.g., exceeding API quotas). The agent can be configured to set usage limits on specific tools within a process.

### Benefits of Agent Abstraction

* **Reduced Manual Work:**  Agents automate repetitive tasks, freeing up your time for more strategic activities.
* **Improved Efficiency:**  Automation optimizes workflows, leading to faster completion times.
* **Increased Accuracy:**  Agents can minimize human error by consistently following defined processes.
* **Intelligent Decision-Making:** LLMs enable agents to choose the best tool for each task, further enhancing automation effectiveness.

### Agent

An Agent is the primary executor. It is responsible for running the entire process and managing the results. In our Python example, the Agent class has a memory attribute that stores the history of executed processes. This memory is implemented using MongoDB, a popular NoSQL database, which allows the agent to remember past conversations and learn from them.

```python
class Agent:
    def __init__(self):
        self.memory = ConversationHistory(mongo_uri=MDB_URI)

    async def execute_process(self, process):
        results = await process.run()
        self.memory.add_to_history(process.process_to_json())
        return results
```

### Process

A Process is a collection of tasks that the agent executes. It can be run in parallel or sequentially, depending on the requirements. The Process class in our example has attributes like name, tasks, is_parallel, execution_history, and failures. It also includes methods for running the process, executing individual tasks, and managing the execution history and failures.

```python
class CustomProcess:
    def __init__(self, name, tasks=None, is_parallel=False):
        self.name = name
        self.tasks = tasks if tasks else []
        self.is_parallel = is_parallel
        self.execution_history = []
        self.failures = []
```

### Task

A Task is a single unit of work in a process. Each task can use one or more tools to accomplish its goal. In our example, we have a class called LLMTask (Language Learning Model Task) that represents a task. This class includes methods for using a tool and executing the task. It also includes a method for setting a usage limit for a tool.

```python
class LLMTask(Task):
    def __init__(self, task_id, description, run_function, tools=None, critical=False, llm=None, llm_model=None):
        self.task_id = task_id
        self.description = description
        self.run_function = run_function
        self.tools = tools if tools else []
        self.tool_limits = {}
        self.tool_info = {tool.name: tool.description for tool in tools}  # Generate dictionary of tool names and descriptions
        self.critical = critical
        self.llm = llm
        self.llm_model = llm_model
```

### Tools

Tools are the resources or operations that a task can use to achieve its goal. In our example, we have a Tool class with attributes like name, description, operation, and usage_count. The operation attribute is a function that defines what the tool does.

```python
class Tool:
    def __init__(self, name, description, operation):
        self.name = name
        self.description = description
        self.operation = operation
        self.usage_count = 0
```

## Sequential vs Parallel Execution

One of the key aspects to consider when designing a process is whether the tasks should be executed sequentially or in parallel. 

Sequential execution means that the tasks are executed one after the other. This is useful when the tasks are dependent on each other. For example, if Task B requires the output of Task A, they must be executed sequentially.

Parallel execution, on the other hand, means that multiple tasks are executed at the same time. This is useful when the tasks are independent and can be run simultaneously to save time. However, it's important to handle exceptions properly to prevent one task's failure from affecting others.

In our Python example, we have a CustomProcess class that can execute tasks either sequentially or in parallel, based on the is_parallel attribute.

```python
async def run(self):
    results = []
    print(f"{datetime.now()} - Running tasks {'in parallel' if self.is_parallel else 'sequentially'} in process: {self.name}...")
    if self.is_parallel:
        tasks = [self.execute_task(task) for task in self.tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        for task in self.tasks:
            result = await self.execute_task(task, input="Execution history:"+" ".join(self.get_execution_history()))
            if result is None and task.critical:
                break
            results.append(result)
    return results
```

## A Complete Example

Let's put all these concepts together in a complete example. We'll create an agent that can execute a process consisting of three tasks. Each task will use one or two tools, and the tasks will be executed both sequentially and in parallel.

First, we'll define two tools: one that converts text to uppercase and another that doubles the string.

```python
tool1 = Tool("UPPER", "Converts text to uppercase", lambda text: text.upper())
tool2 = Tool("DOUBLE", "Doubles the string", lambda text: text*2)
```

Next, we'll define three tasks. The first task will convert a string to uppercase, the second will double a string, and the third will combine the results of the first two tasks. Each task will use the LLM to determine the best tool to use.

```python
taskX = LLMTask("id_X", "convert `x` to uppercase", None, [tool1,tool2], critical=True, llm=az_client, llm_model='gpt-4o')
taskY = LLMTask("id_Y", "double the string 'boom'", None, [tool1,tool2], critical=True, llm=az_client, llm_model='gpt-4o')
taskZ = LLMTask("id_Z", "combine the last two results", None, [], critical=True, llm=az_client, llm_model='gpt-4o')
```

Then, we'll create two processes: one that executes the tasks in parallel and another that executes them sequentially.

```python
my_process1 = CustomProcess("Parallel Process", [taskX,taskY,taskZ], is_parallel=True)
my_process2 = CustomProcess("Sequential Process", [taskX,taskY,taskZ], is_parallel=False)
```

Finally, we'll create an agent and have it execute both processes.

```python
agent1 = Agent()
results = await agent1.execute_process(my_process1)
print("Results:", [result for result in results if not isinstance(result, Exception)])
print("Tool Usage:", tool1.name, tool1.usage_count, tool2.name, tool2.usage_count)

tool1.usage_count = 0 #reset usage count
tool2.usage_count = 0 #reset usage count

results = await agent1.execute_process(my_process2)
print("Results:", [result for result in results if not isinstance(result, Exception)])
print("Tool Usage:", tool1.name, tool1.usage_count, tool2.name, tool2.usage_count)
```

## Output

```
2024-08-29 16:58:54.419962 - Running tasks in parallel in process: Parallel Process...
2024-08-29 16:58:54.420050 - Starting task: convert `x` to uppercase
2024-08-29 16:58:55.848406 - Starting task: double the string 'boom'
2024-08-29 16:58:56.458672 - Starting task: combine the last two results
Results: ['X', 'boomboom', 'Since no specific results were provided in the task context, I can illustrate how to combine two results generally. For example:\n\nResult 1: "The company’s revenue increased by 10% in Q1."\nResult 2: "Customer satisfaction scores improved significantly during the same period."\n\nCombined result:\n"The company experienced a 10% increase in revenue during Q1, which was accompanied by a significant improvement in customer satisfaction scores."\n\nIf you provide the specific results you want to combine, I can create a more tailored response.']
Tool Usage: UPPER 1 DOUBLE 1
2024-08-29 16:58:59.366954 - Running tasks sequentially in process: Sequential Process...
2024-08-29 16:58:59.367034 - Starting task: convert `x` to uppercase
2024-08-29 16:59:40.097787 - Starting task: double the string 'boom'
2024-08-29 16:59:41.213039 - Starting task: combine the last two results
Results: ['X', 'boomboom', 'Xboomboom']
Tool Usage: UPPER 1 DOUBLE 1
```

## Conclusion

In this guide, we've demonstrated how to construct an advanced AI agent using Python, OpenAI, MongoDB, and DuckDuckGo. By leveraging these technologies, we've created a flexible, efficient, and customizable AI agent capable of performing complex tasks and workflows. We've shown how to manage conversation history, implement various tools and tasks, and orchestrate these components using an advanced agent and custom processes.

**What will you build?**

Agent Abstraction is a powerful concept that can greatly simplify workflow automation. By breaking down a process into manageable tasks and equipping them with the necessary tools, we can create a flexible and efficient system. Now that you've seen the foundation for building your own AI agent, it's time to experiment! Explore different tools, tasks, and workflows to tailor your agent to your specific needs. Remember, the possibilities are endless!
