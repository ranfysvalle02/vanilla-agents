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
    def __init__(self, mongo_uri=None):
        # If MongoDB URI is provided, connect to MongoDB
        if mongo_uri:
            self.client = pymongo.MongoClient(mongo_uri)
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]

    def add_to_history(self, history_object, is_user=True):
        """
        Add a new entry to the conversation history.
        """
        # If MongoDB client is available, insert the conversation into MongoDB
        if self.client:
            self.collection.insert_one(history_object)
 
class Tool:
    def __init__(self, name, description, operation):
        self.name = name
        self.description = description
        self.operation = operation
        self.usage_count = 0

    def run(self, input):
        return self.operation(input)
class Task:
    def __init__(self, task_id, description, run_function, tools=None, critical=False):
        self.task_id = task_id
        self.description = description
        self.run_function = run_function
        self.tools = tools if tools else []
        self.tool_limits = {}
        self.critical = critical

    async def use_tool(self, tool_name, input):
        tool = next((tool for tool in self.tools if tool.name == tool_name), None)
        if not tool:
            raise Exception(f"No tool found with name: {tool_name}")
        if tool_name in self.tool_limits and self.tool_limits[tool_name] <= tool.usage_count:
            raise Exception(f"Usage limit exceeded for tool: {tool.name} in task: {self.description}")
        tool.usage_count += 1
        return tool.run(input)

    async def execute(self, input=None):
        result = await self.run_function(input)
        for tool in self.tools:
            result = await self.use_tool(tool.name, result)
        print(f"{datetime.now()} - Finished task: {self.description}")
        return result

    def set_tool_limit(self, tool_name, limit):
        self.tool_limits[tool_name] = limit
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

    async def use_tool(self, tool_name, input):
        tool = next((tool for tool in self.tools if tool.name == tool_name), None)
        if not tool:
            raise Exception(f"No tool found with name: {tool_name}")
        if tool_name in self.tool_limits and self.tool_limits[tool_name] <= tool.usage_count:
            raise Exception(f"Usage limit exceeded for tool: {tool.name} in task: {self.description}")
        tool.usage_count += 1
        return tool.run(input)

    async def execute(self, input=None):
        print(f"{datetime.now()} - Starting task: {self.description}")
        if self.llm:
            ai_msg = self.llm.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": """
You are a helpful assistant that can help determine the best `tool` to use for a given `input` string.
"""},
                    {"role": "user", "content": f"""
What is the best tool to use given this input

Input: `{self.description}`

[available tools]
{self.tool_info}

[IMPORTANT! ONLY SELECT A TOOL FROM THE AVAILABLE TOOLS! IF NO TOOL IS AVAILABLE, DO NOT MAKE IT UP!]

[response format]
JSON response must have: 
 `tool_id` key with the `id` of the tool.
 `tool_input` key with the input that should be passed to the tool.
 `original_input` key with the original input: `{input}` 
"""}
                ], 
                response_format={ "type": "json_object" }
            )
            result = json.loads(ai_msg.choices[0].message.content)
            tool_input = result.get("tool_input")
            tool_id = result.get("tool_id")
            if result:
                if self.run_function:
                    result = await self.run_function(input)
                if tool_id:
                    for tool in self.tools:
                        if tool.name in tool_id:
                            result = await self.use_tool(tool.name, tool_input)
                            break
                else:
                    # if no tool usage, lets respond with what we have
                    result = self.llm.chat.completions.create(
                        model=self.llm_model,
                        messages=[
                            {"role": "system", "content": f"""
[task context]:
{input}
[end task context]

[task description]:
{self.description}

[IMPORTANT!]
USE THE AVAILABLE CONTEXT WHEN APPLICABLE TO GENERATE YOUR RESPONSE!
"""}
                        ]
                    )
                    result = result.choices[0].message.content
        else:
            result = await self.run_function(input)
            for tool in self.tools:
                result = await self.use_tool(tool.name, result)
            print(f"{datetime.now()} - Finished task: {self.description}")
        return result

    def set_tool_limit(self, tool_name, limit):
        self.tool_limits[tool_name] = limit

class CustomProcess:
    def __init__(self, name, tasks=None, is_parallel=False):
        self.name = name
        self.tasks = tasks if tasks else []
        self.is_parallel = is_parallel
        self.execution_history = []
        self.failures = []
    def process_to_json(self):
        """
        Convert a CustomProcess object to a JSON object.
        """
        process_dict = {
            "name": self.name,
            "is_parallel": self.is_parallel,
            "tasks": []
        }
        
        for task in self.tasks:
            task_dict = {
                "task_id": task.task_id,
                "description": task.description,
                "tools": []
            }
            
            for tool in task.tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description
                }
                task_dict["tools"].append(tool_dict)
            
            process_dict["tasks"].append(task_dict)
        process_dict["timestamp"] = datetime.now()
        process_dict["execution_history"] = self.get_execution_history()
        process_dict["failures"] = self.get_failures()

        return process_dict
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

    async def execute_task(self, task, input=None):
        try:
            result = await task.execute(input)
            self.execution_history.append(str({
                "task_id": task.task_id,
                "description": task.description,
                "result": result,
                "task_input": input
            }))
            return result
        except Exception as error:
            print(f"{datetime.now()} - Error executing task: {task.description} in process: {self.name}", error)
            self.failures.append(f"Failure in process {self.name}: {str(error)}")
            if task.critical:
                print(f"{datetime.now()} - Critical task failed. Exiting process: {self.name}")
                return None
            return error

    def add_task(self, task, repetitions=1):
        self.tasks.extend([task]*repetitions)

    def clear_tasks(self):
        self.tasks.clear()
        self.execution_history.clear()
        self.failures.clear()

    def get_execution_history(self):
        return self.execution_history.copy()

    def get_failures(self):
        return self.failures.copy()

class Agent:
    def __init__(self):
        self.memory = ConversationHistory(mongo_uri=MDB_URI)
    async def execute_process(self, process):
        results = await process.run()
        self.memory.add_to_history(process.process_to_json())
        return results

async def main():
    tool1 = Tool("UPPER", "Converts text to uppercase", lambda text: text.upper())
    tool2 = Tool("DOUBLE", "Doubles the string", lambda text: text*2)

    taskX = LLMTask("id_X", "convert `x` to uppercase", None, [tool1,tool2], critical=True, llm=az_client, llm_model='gpt-4o')
    taskY = LLMTask("id_Y", "double the string 'boom'", None, [tool1,tool2], critical=True, llm=az_client, llm_model='gpt-4o')
    taskZ = LLMTask("id_Z", "combine the last two results", None, [], critical=True, llm=az_client, llm_model='gpt-4o')

    my_process1 = CustomProcess("Parallel Process", [taskX,taskY,taskZ], is_parallel=True)
    agent1 = Agent()
    results = await agent1.execute_process(my_process1)
    print("Results:", [result for result in results if not isinstance(result, Exception)])
    print("Tool Usage:", tool1.name, tool1.usage_count, tool2.name, tool2.usage_count)
    tool1.usage_count = 0 #reset usage count
    tool2.usage_count = 0 #reset usage count
    my_process2 = CustomProcess("Sequential Process", [taskX,taskY,taskZ], is_parallel=False)
    agent1 = Agent()
    results = await agent1.execute_process(my_process2)
    print("Results:", [result for result in results if not isinstance(result, Exception)])
    print("Tool Usage:", tool1.name, tool1.usage_count, tool2.name, tool2.usage_count)

asyncio.run(main())
