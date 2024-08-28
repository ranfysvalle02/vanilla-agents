## Building an Advanced AI Agent with OpenAI, MongoDB, and DuckDuckGo

![AI Agent Overview](https://upload.wikimedia.org/wikipedia/commons/a/aa/AI_Agent_Overview.png)

## Introducing `vanilla-agents`

`vanilla-agents` provides a lightweight and customizable implementation that empowers you to leverage the capabilities of your preferred large language model (LLM) provider without the need for additional, often bloated libraries. 

The flow of operation is as follows: User Input -> Start Process -> Task Execution -> Tool Selection -> Complete Process -> Response. With just a few well-placed lines of code, you can take control and build a custom AI agent that bends to your will and can implement custom processes/workflows. 

## Breaking Down the Tasks into a Custom Process

The system is designed to perform two main tasks:

* **Task 1: Search for YouTube Videos**
  * This task involves identifying relevant YouTube videos based on a given query or topic.
* **Task 2: Write a Report**
  * This task requires writing a report based on the content of the videos found in Task 1.

These tasks are combined into a cohesive workflow using a `CustomProcess`:

1. **Retrieves Videos:** The first task searches for videos based on a user-provided query.
2. **Writes a Report:** The second task generates a report from the content of the retrieved videos.

Here's how these tasks are defined in the code:

```python
task1 = Task(
    description=str("Perform a search for: `"+user_input+"`"),
    agent=AdvancedAgent(
        tools=[SearchTool("search", "Search the web.")],
        history=ConversationHistory(MDB_URI)
    ),
    name="step_1",
    tool_use_required=True
)

task2 = Task(
    description=f"""
Write a concise bullet point report on `{user_input}` using the provided [task_context].
IMPORTANT! Use the [task_context]

[Response Criteria]:
- Bullet point summary
- Minimum of 100 characters
- Use the provided [task_context]

""",
    agent=AdvancedAgent(
        history=ConversationHistory(MDB_URI),
        tools=[]
    ),
    input=task1,
    name="step_2"
)
```

The `CustomProcess` class allows you to chain tasks together, creating more complex workflows. The `run` method of the `CustomProcess` class executes all tasks in the process asynchronously. Here's how the `CustomProcess` is defined and used in the code:

```python
class CustomProcess:
    """
    Class representing a process that consists of multiple tasks.
    """
    def __init__(self, tasks):
        self.tasks = tasks

    async def run(self):
        """
        Runs all tasks in the process asynchronously.
        """
        results = []
        for i, task in enumerate(self.tasks):
            result = await task.run()  # Pass the result of the previous task to the next task
            results.append(result)
        print("Process complete.")
        return results

# Create process
my_process = CustomProcess([task1, task2])

# Run process and print the result
result = await my_process.run()
print(result[-1].get("answer", ""))
```

In this example, `my_process` is an instance of `CustomProcess` that includes `task1` and `task2`. When `my_process.run()` is called, it executes `task1` and `task2` in sequence. The result of each task is stored in the `results` list, and the final result is printed out.

## Key Components and How They Work

### Tools

`Tools` are the fundamental units of functionality. They are akin to specialized capabilities that the agent can utilize. For instance, the `SearchTool` in our code leverages DuckDuckGo to retrieve information from the web. 

Each tool is a class that inherits from the base `Tool` class and implements a `run` method. This method encapsulates the specific functionality of the tool. Here's how the `SearchTool` is defined:

```python
class SearchTool(Tool):
    """
    Tool to search the web using DuckDuckGo.
    """
    def run(self, input):
        """
        Runs a DuckDuckGo search and returns the results.
        """
        results = DDGS().text(str(input+" site:youtube.com video"), region="us-en", max_results=5)
        return {"web_search_results": results, "input": input, "tool_id": "<" + self.name + ">"}
```

### Tasks

`Tasks` are the specific actions that the agent can perform. They are defined as instances of the `Task` class, which includes a `run` method that defines how the task is performed. Each task is designed to use one or more tools to accomplish a specific goal. 

### AdvancedAgent

The `AdvancedAgent` is the core component that orchestrates the tools and tasks. It's responsible for understanding user prompts, selecting appropriate tools, and managing the conversation history. The agent uses the OpenAI API to generate text based on a given prompt and can use tools to assist in generating responses.

```python
class AdvancedAgent:
    """
    Advanced agent that can use tools and maintain conversation history.
    """
    def __init__(self, model="gpt-4o", history=None, tools=[]):
        self.openai = az_client
        self.model = model
        self.history = history or ConversationHistory()  # Use provided history or create new one
        self.tools = tools
        self.tool_info = {tool.name: tool.description for tool in tools}  # Generate dictionary of tool names and descriptions
```

### CustomProcess

The `CustomProcess` class allows you to chain tasks together, creating more complex workflows. For instance, you could define a process that first searches for information and then writes a report based on the search results. The `run` method of the `CustomProcess` class executes all tasks in the process asynchronously.

```python
class CustomProcess:
    """
    Class representing a process that consists of multiple tasks.
    """
    def __init__(self, tasks):
        self.tasks = tasks
```

### Memory

Memory in this context refers to the conversation history managed by the `ConversationHistory` class. This class can either store the history in memory or use MongoDB to persist the history. While the memory doesn't directly influence the agent's responses in this implementation, it plays a crucial role in maintaining a record of the agent's activities.

```python
class ConversationHistory:
    """
    Class to manage conversation history, either in memory or using MongoDB.
    """
    def __init__(self, mongo_uri=None):
        self.history = []  # Default to in-memory list if no Mongo connection

        # If MongoDB URI is provided, connect to MongoDB
        if mongo_uri:
            self.client = pymongo.MongoClient(mongo_uri)
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
```


## How the Agent Uses the CustomProcess

The agent uses the `CustomProcess` to execute a series of tasks in a specific order. Each task in the process is executed asynchronously, and the results of each task are stored and can be used as input for subsequent tasks. 

The agent creates a `CustomProcess` that includes two tasks: `task1` and `task2`. When the agent calls `my_process.run()`, it executes `task1` and `task2` in sequence. The result of each task is stored in the `results` list, and the final result is printed out.

## MongoDB as Data Platform

The agent interacts with MongoDB through the `ConversationHistory` class. This class is used to manage the conversation history, either in memory or using MongoDB. If a MongoDB URI is provided, the class connects to MongoDB and uses it to persist the conversation history. 

The agent talks to MongoDB every time it adds a new entry to the conversation history. This happens in the `add_to_history` method of the `ConversationHistory` class:

```python
def add_to_history(self, text, is_user=True):
    """
    Add a new entry to the conversation history.
    """
    timestamp = datetime.now().isoformat()
    # If MongoDB client is available, insert the conversation into MongoDB
    if self.client:
        self.collection.insert_one({"text": text, "is_user": is_user, "timestamp": timestamp})
    else:
        self.history.append((text, is_user, timestamp))
```

## Creating Your Own Tool or Task

Creating your own tool or task is straightforward. 

To create a new tool, you need to define a new class that inherits from the `Tool` class and implement the `run` method. This method should encapsulate the specific functionality of your tool. Here's a template you can use:

```python
class MyTool(Tool):
    """
    My custom tool.
    """
    def run(self, input):
        """
        Implement the functionality of the tool here.
        """
        # Your code here
        return result
```

To create a new task, you need to create an instance of the `Task` class and provide the necessary parameters. This includes a description of the task, the agent that will perform the task, any tools that the task should use, and any input that the task requires. Here's a template you can use:

```python
my_task = Task(
    description="My task description",
    agent=my_agent,
    tools=[my_tool],
    input=my_input,
    name="my_task"
)
```

## The Benefits of a Lightweight Approach

* **Flexibility:** You have full control over the components and their interactions. This allows you to tailor the agent to your specific needs.
* **Efficiency:** By avoiding unnecessary dependencies, you can maintain a lean and efficient implementation.
* **Customization:** You can easily add or remove tools and tasks as required, making the AI highly adaptable.
* **Control:** You have direct access to the code, enabling you to fine-tune behavior and troubleshoot issues.

## Conclusion

Now that you've seen the foundation for building your own AI agent, it's time to experiment!
