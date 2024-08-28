## Building an Advanced AI Agent with OpenAI, MongoDB, and DuckDuckGo
![](https://upload.wikimedia.org/wikipedia/commons/a/aa/AI_Agent_Overview.png)

Contrary to popular belief, crafting a generative AI *agent* doesn't require a mountain of complex libraries. With just a few well-placed lines of code, you can take control and build a custom AI agent that bends to your will and can implement custom processes/workflows. Intrigued? This guide will equip you with the building blocks to forge your very own generative AI agent from scratch, giving you the freedom to experiment and innovate.

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

**The Benefits of a Lightweight Approach:**

* **Flexibility:** You have full control over the components and their interactions. This allows you to tailor the AI to your specific needs.
* **Efficiency:** By avoiding unnecessary dependencies, you can maintain a lean and efficient implementation.
* **Customization:** You can easily add or remove tools and tasks as required, making the AI highly adaptable.
* **Control:** You have direct access to the code, enabling you to fine-tune behavior and troubleshoot issues.

**How It Works:**

1. **User Input:** The user provides a prompt or question.
2. **Tool Selection:** The `AdvancedAgent` analyzes the prompt and determines the most suitable tools to use.
3. **Task Execution:** The selected tools are employed to carry out the necessary tasks.
4. **Response Generation:** The `AdvancedAgent` combines the results from the tools and generates a response.

**The Foundation: Setting Up the Environment**

Our first step is to set up our environment. This involves importing necessary libraries and defining some constants. We're using libraries like `openai` for AI model interaction, `pymongo` for database management, `duckduckgo_search` for web search, and `youtube_transcript_api` for fetching YouTube video transcripts.

```python
import json
from openai import AzureOpenAI
import pymongo
from duckduckgo_search import DDGS
import asyncio
from datetime import datetime
import re
from youtube_transcript_api import YouTubeTranscriptApi
...
```

**The Memory: Conversation History Management**

As our AI assistant interacts with users, it's crucial to remember past conversations. We create a `ConversationHistory` class to manage this memory, storing it either in a local list or a MongoDB database for more persistent storage.

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

	def get_history(self):
    	"""
    	Get the conversation history as a formatted string.
    	"""
    	if self.client:
        	history = self.collection.find({}, sort=[("timestamp", pymongo.DESCENDING)]).limit(2)
        	return "\n".join([f"{item['timestamp']} - {'User' if item.get('is_user', False) else 'Assistant'}: {item['text']}" for item in history])
    	else:
        	return "\n".join([f"{timestamp} - {'User' if is_user else 'Assistant'}: {text}" for text, is_user, timestamp in self.history])
```

**The Skills: Tools and Tasks**

Our AI assistant needs skills to perform tasks. We represent these skills as `Tool` objects. For instance, we have a `SearchTool` that uses the DuckDuckGo search engine to retrieve information from the web.

```python
class Tool:
	"""
	Base class for tools that the agent can use.
	"""
	def __init__(self, name, description):
    	self.name = name
    	self.description = description
    	self.openai = az_client
    	self.model = "gpt-4o"

	def run(self, input):
    	"""
    	This method needs to be implemented by specific tool classes.
    	"""
    	raise NotImplementedError("Tool must implement a run method")

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
**The Actions: Tasks**

```python
class Task:
	"""
	Class representing a task for the agent to complete.
	"""
	def __init__(self, description, agent, tools=[], input=None, name="", tool_use_required=False):
    	self.description = description
    	self.agent = agent
    	self.tools = tools
    	self.output = None
    	self.input = input
    	self.name = name
    	self.tool_use_required = tool_use_required

	async def run(self):
    	"""
    	Runs the task using the agent and tools, optionally adding additional context.
    	"""
    	# Use the agent and tools to perform the task
    	if self.input:
        	self.description += "\nUse this task_context to complete the task:\n[task_context]\n" + str(self.input.output) + "\n[end task_context]\n"
    	result = await self.agent.generate_text(self.description)
    	self.output = result
    	return result
```

Tasks are the actions that our AI assistant can perform using its skills. For example, a task could be to search for information on a specific topic and summarize the findings. Each task is represented as an instance of the `Task` class, which includes a description of the task, the agent that will perform the task, the tools that the agent will use, and the input that the task will process.

**The Brain: Advanced Agent and Custom Process**

The `AdvancedAgent` is the brain of our AI assistant. It orchestrates the use of tools and tasks, generates responses to user prompts, and maintains the conversation history.

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

	async def generate_text(self, prompt):
    	"""
    	Generates text using the provided prompt, considering conversation history and tool usage.
    	"""
    	response = self.openai.chat.completions.create(
        	messages=[
            	{"role": "user", "content": "Given this prompt:`" + prompt + "`"},
            	{"role": "user", "content": """
What tool would best help you to respond? If no best tool, just provide an answer to the best of your ability.
Return an empty array if you don't want to use any tool for the `tools` key.

AVAILABLE TOOLS: """ + ', '.join([f'"{name}": "{desc}"' for name, desc in self.tool_info.items()]) + """

ALWAYS TRY TO USE YOUR TOOLS FIRST!

[RESPONSE CRITERIA]:
- JSON object
- Format: {"tools": ["tool_name"], "prompt": "user input without the command", "answer": "answer goes here"}

[EXAMPLE]:
{"tools": ["search"], "prompt": "[user input without the command]", "answer": "<search>"}
{"tools": [], "prompt": "[user input without the command]", "answer": "..."}
"""}
        	],
        	model=self.model,
        	response_format={"type": "json_object"}
    	)
    	# add question to history
    	self.history.add_to_history(prompt, is_user=True)

    	ai_response = json.loads(response.choices[0].message.content.strip())
    	if not ai_response.get("tools", []):
        	self.history.add_to_history(ai_response.get("answer", ""), is_user=False)
        	return ai_response
    	# Process the response (consider using tools here based on AI suggestion)
    	tools_to_use = ai_response.get("tools", [])
    	clean_prompt = ai_response.get("prompt", "")
    	for tool_name in tools_to_use:
        	tool = next((t for t in self.tools if t.name == tool_name), None)
        	if tool:
            	if tool_name == "search":
                	ai_response = tool.run(clean_prompt)
           	 

    	self.history.add_to_history(ai_response, is_user=False)
    	return ai_response

```

## **Expanding on `response_format={"type": "json_object"}`**

By structuring responses in JSON format, you're essentially providing a blueprint for how the AI's thoughts can be interpreted and processed. The use of `response_format={"type": "json_object"}` when interacting with the OpenAI API is crucial for providing clear instructions to the AI model and receiving structured responses. Let's delve deeper into its significance and benefits.

### **Why JSON Objects?**

* **Clarity and Structure:** JSON objects offer a human-readable and machine-processable format for organizing data. This makes it easier to parse and interpret the model's responses.
* **Flexibility:** JSON can represent a wide range of data types, including strings, numbers, arrays, and objects. This flexibility allows for complex responses and customization.
* **Consistent Format:** By specifying the `json_object` response format, you ensure that the model's output adheres to a predictable structure, simplifying subsequent processing.

### **Key Components of the JSON Object**

When using the `json_object` format, the AI model's response typically includes the following components:

* **`tools`:** An array of tool names that the model suggests using to complete the task. Empty array if no tool.
* **`prompt`:** The refined prompt that the model will use after considering the available tools. [no command]
* **`answer`:** The generated response, which might be a direct answer or an instruction to use one of the suggested tools.

### **Example Response**

```json
{
  "tools": ["search"],
  "prompt": "What is the capital of France?",
  "answer": "<search>"
}
```

**The Workflow: Custom Process**

Sometimes, our AI assistant needs to perform a series of tasks in a specific order. That's where the `CustomProcess` class comes in. It allows us to chain tasks together to create more complex workflows. For instance, we might have a process that involves searching for information, analyzing the results, and then summarizing the findings.

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
        	if task.input and task.input.output:
            	if task.name == "step_2":
                	alltext = ""
                	for yt_result in task.input.output["web_search_results"]:
                    	video_id = extract_youtube_id_from_href(yt_result["href"])
                    	if video_id:
                        	try:
                            	transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            	if transcript:
                                	alltext = (' '.join(item['text'] for item in transcript))
                                	task.description += f"""\nYoutube Transcript for {video_id}:\n""" + alltext
                                	print(f"Added transcript for {video_id}")
                        	except Exception as e:
                            	print(f"Error fetching transcript for {video_id}")
        	result = await task.run()  # Pass the result of the previous task to the next task
        	results.append(result)
    	print("Process complete.")
    	return results
```

**The Adventure: Running the AI Assistant**

With all the components in place, it's time to set our AI assistant in motion. We create tasks, chain them into a process, and set the process running. As the tasks are performed, our AI assistant interacts with the user, remembers the conversation, and uses its tools to generate responses.

```python
async def main():
	# Use a MongoDB connection string for persistent history (optional)
	# Create tasks
	user_input = input("Enter any topic: ")
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

	# Create process
	my_process = CustomProcess([task1, task2])

	# Run process and print the result
	result = await my_process.run()
	print(result[-1].get("answer", ""))

if __name__ == "__main__":
	asyncio.run(main())
```

## FULL CODE

```python
import json
from openai import AzureOpenAI
import pymongo
from duckduckgo_search import DDGS
import asyncio
from datetime import datetime
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Define constants
AZURE_OPENAI_ENDPOINT = "https://.openai.azure.com"
AZURE_OPENAI_API_KEY = ""
az_client = AzureOpenAI(azure_endpoint=AZURE_OPENAI_ENDPOINT,api_version="2023-07-01-preview",api_key=AZURE_OPENAI_API_KEY)
MDB_URI = ""
DB_NAME = ""
COLLECTION_NAME = "agent_history"

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

	def get_history(self):
    	"""
    	Get the conversation history as a formatted string.
    	"""
    	if self.client:
        	history = self.collection.find({}, sort=[("timestamp", pymongo.DESCENDING)]).limit(2)
        	return "\n".join([f"{item['timestamp']} - {'User' if item.get('is_user', False) else 'Assistant'}: {item['text']}" for item in history])
    	else:
        	return "\n".join([f"{timestamp} - {'User' if is_user else 'Assistant'}: {text}" for text, is_user, timestamp in self.history])

class Tool:
	"""
	Base class for tools that the agent can use.
	"""
	def __init__(self, name, description):
    	self.name = name
    	self.description = description
    	self.openai = az_client
    	self.model = "gpt-4o"

	def run(self, input):
    	"""
    	This method needs to be implemented by specific tool classes.
    	"""
    	raise NotImplementedError("Tool must implement a run method")

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

class Task:
	"""
	Class representing a task for the agent to complete.
	"""
	def __init__(self, description, agent, tools=[], input=None, name="", tool_use_required=False):
    	self.description = description
    	self.agent = agent
    	self.tools = tools
    	self.output = None
    	self.input = input
    	self.name = name
    	self.tool_use_required = tool_use_required

	async def run(self):
    	"""
    	Runs the task using the agent and tools, optionally adding additional context.
    	"""
    	# Use the agent and tools to perform the task
    	if self.input:
        	self.description += "\nUse this task_context to complete the task:\n[task_context]\n" + str(self.input.output) + "\n[end task_context]\n"
    	result = await self.agent.generate_text(self.description)
    	self.output = result
    	return result

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
        	if task.input and task.input.output:
            	if task.name == "step_2":
                	alltext = ""
                	for yt_result in task.input.output["web_search_results"]:
                    	video_id = extract_youtube_id_from_href(yt_result["href"])
                    	if video_id:
                        	try:
                            	transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            	if transcript:
                                	alltext = (' '.join(item['text'] for item in transcript))
                                	task.description += f"""\nYoutube Transcript for {video_id}:\n""" + alltext
                                	print(f"Added transcript for {video_id}")
                        	except Exception as e:
                            	print(f"Error fetching transcript for {video_id}")
        	result = await task.run()  # Pass the result of the previous task to the next task
        	results.append(result)
    	print("Process complete.")
    	return results

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

	async def generate_text(self, prompt):
    	"""
    	Generates text using the provided prompt, considering conversation history and tool usage.
    	"""
    	response = self.openai.chat.completions.create(
        	messages=[
            	{"role": "user", "content": "Given this prompt:`" + prompt + "`"},
            	{"role": "user", "content": """
What tool would best help you to respond? If no best tool, just provide an answer to the best of your ability.
Return an empty array if you don't want to use any tool for the `tools` key.

AVAILABLE TOOLS: """ + ', '.join([f'"{name}": "{desc}"' for name, desc in self.tool_info.items()]) + """

ALWAYS TRY TO USE YOUR TOOLS FIRST!

[RESPONSE CRITERIA]:
- JSON object
- Format: {"tools": ["tool_name"], "prompt": "user input without the command", "answer": "answer goes here"}

[EXAMPLE]:
{"tools": ["search"], "prompt": "[user input without the command]", "answer": "<search>"}
{"tools": [], "prompt": "[user input without the command]", "answer": "..."}
"""}
        	],
        	model=self.model,
        	response_format={"type": "json_object"}
    	)
    	# add question to history
    	self.history.add_to_history(prompt, is_user=True)

    	ai_response = json.loads(response.choices[0].message.content.strip())
    	if not ai_response.get("tools", []):
        	self.history.add_to_history(ai_response.get("answer", ""), is_user=False)
        	return ai_response
    	# Process the response (consider using tools here based on AI suggestion)
    	tools_to_use = ai_response.get("tools", [])
    	clean_prompt = ai_response.get("prompt", "")
    	for tool_name in tools_to_use:
        	tool = next((t for t in self.tools if t.name == tool_name), None)
        	if tool:
            	if tool_name == "search":
                	ai_response = tool.run(clean_prompt)
           	 

    	self.history.add_to_history(ai_response, is_user=False)
    	return ai_response


def extract_youtube_id_from_href(href_url):
	# Split the URL on the '=' character
	url_parts = href_url.split('=')
	# The video ID is the part after 'v', which is the last part of the URL
	video_id = url_parts[-1]
	return video_id



async def main():
	# Use a MongoDB connection string for persistent history (optional)
	# Create tasks
	user_input = input("Enter any topic: ")
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

	# Create process
	my_process = CustomProcess([task1, task2])

	# Run process and print the result
	result = await my_process.run()
	print(result[-1].get("answer", ""))

if __name__ == "__main__":
	asyncio.run(main())
```

**What will you build?**

In this guide, we've demonstrated how to construct an advanced AI agent using Python, OpenAI, MongoDB, and DuckDuckGo. By leveraging these technologies, we've created a flexible, efficient, and customizable AI agent capable of performing complex tasks and workflows. We've shown how to manage conversation history, implement various tools and tasks, and orchestrate these components using an advanced agent and custom processes.

Now that you've seen the foundation for building your own AI agent, it's time to experiment! Explore different tools, tasks, and workflows to tailor your agent to your specific needs. Remember, the possibilities are endless!
