## Building an Advanced AI Agent with OpenAI, MongoDB, and DuckDuckGo

![](https://upload.wikimedia.org/wikipedia/commons/a/aa/AI_Agent_Overview.png)

**Introducing `vanilla-agents`**

**User Input -> Start Process -> Task Execution -> Tool Selection -> Complete Process -> Response**

`vanilla-agents` provides a lightweight and customizable implementation that empowers you to leverage the capabilities of your preferred LLM provider without the need for additional, often bloated libraries. 

With just a few well-placed lines of code, you can take control and build a custom AI agent that bends to your will and can implement custom processes/workflows. 

## Breaking Down the Tasks into a Custom Process

* **Task 1: Search for YouTube Videos**
  * This task involves identifying relevant YouTube videos based on a given query or topic.
* **Task 2: Summarize the Content**
  * This task requires extracting the transcripts, key points and ideas from the videos found in Task 1.

**Creating a Custom Process:**

To combine these tasks into a cohesive workflow, we can define a `CustomProcess` that:

1. **Retrieves Videos:** search for videos based on a user-provided query.
2. **Extracts Content:** extract the transcripts of the retrieved videos.
3. **Summarizes Content:** generate summaries from the extracted transcripts.

**Key Components and How They Work:**

1. **Tools:** These are the building blocks of your AI's functionality. Think of them as specialized skills. For instance, a `SearchTool` might leverage DuckDuckGo to retrieve information from the web.
2. **Tasks:** These are the specific actions your AI can perform. A task might involve using multiple tools in sequence. For example, a "Summarize" task could use a `SearchTool` to gather information and then employ a summarization technique.
3. **AdvancedAgent:** This is the core component that orchestrates the tools and tasks. It's responsible for understanding user prompts, selecting appropriate tools, and managing the conversation history.
4. **CustomProcess:** This allows you to chain tasks together, creating more complex workflows. For instance, you could define a process that first searches for information and then analyzes it using sentiment analysis.
5. **Memory:** refers to the logging system we've implemented using MongoDB Atlas. This system records the agent's interactions, creating a valuable log that can be used for debugging, performance analysis, and future enhancements. While in this demo the memory doesn't directly influence the agent's responses using context augmentation for contextual awareness, it plays a crucial role in maintaining a record of the agent's activities.

**Key Components Explained**

This section provides an in-depth look at the key components of our agentic abstraction built on top of large language models. 

The system is designed to perform complex tasks and maintain a record of its interactions, leveraging a combination of tools, tasks, and an advanced agent to orchestrate the process.

**Tools: Specialized Capabilities**

In the system, `Tools` are the fundamental units of functionality. They are akin to specialized capabilities that the agent can utilize. For instance, the `SearchTool` in our code leverages DuckDuckGo to retrieve information from the web. 

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

**Tasks: Defined Actions**

`Tasks` are the specific actions that the agent can perform. They are defined as instances of the `Task` class, which includes a `run` method that defines how the task is performed. Each task is designed to use one or more tools to accomplish a specific goal. 

For instance, the following `Task` uses the `SearchTool` to perform a web search based on user input:

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
```

**AdvancedAgent: The Orchestrator**

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

**CustomProcess: Chaining Tasks**

The `CustomProcess` class allows you to chain tasks together, creating more complex workflows. For instance, you could define a process that first searches for information and then writes a report based on the search results. The `run` method of the `CustomProcess` class executes all tasks in the process asynchronously.

```python
class CustomProcess:
    """
    Class representing a process that consists of multiple tasks.
    """
    def __init__(self, tasks):
        self.tasks = tasks
```

**Memory: Conversation History**

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

**The Benefits of a Lightweight Approach:**

* **Flexibility:** You have full control over the components and their interactions. This allows you to tailor the agent to your specific needs.
* **Efficiency:** By avoiding unnecessary dependencies, you can maintain a lean and efficient implementation.
* **Customization:** You can easily add or remove tools and tasks as required, making the AI highly adaptable.
* **Control:** You have direct access to the code, enabling you to fine-tune behavior and troubleshoot issues.

## Conclusion

Now that you've seen the foundation for building your own AI agent, it's time to experiment! 
