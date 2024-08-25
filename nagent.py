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
