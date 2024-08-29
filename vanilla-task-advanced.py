import asyncio
from datetime import datetime

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
        print(f"{datetime.now()} - Starting task: {self.description}")
        result = await self.run_function(input)
        for tool in self.tools:
            result = await self.use_tool(tool.name, result)
        print(f"{datetime.now()} - Finished task: {self.description}")
        return result

    def set_tool_limit(self, tool_name, limit):
        self.tool_limits[tool_name] = limit

class CustomProcess:
    def __init__(self, name, tasks=None, is_parallel=False, entrypoint=None):
        self.name = name
        self.tasks = tasks if tasks else []
        self.is_parallel = is_parallel
        self.execution_history = []
        self.failures = []
        self.entrypoint = entrypoint if entrypoint else lambda x: x

    async def run(self, input_string=None):
        results = []
        input_string = self.entrypoint(input_string)
        print(f"{datetime.now()} - Running tasks {'in parallel' if self.is_parallel else 'sequentially'} in process: {self.name}...")
        if self.is_parallel:
            tasks = [self.execute_task(task, input_string) for task in self.tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            previous_result = input_string
            for task in self.tasks:
                result = await self.execute_task(task, previous_result)
                if result is None and task.critical:
                    break
                results.append(result)
                previous_result = result
        return results

    async def execute_task(self, task, input=None):
        try:
            result = await task.execute(input)
            self.execution_history.append(f"Task executed: {task.description}")
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
        pass

    async def execute_process(self, process, input_string=None):
        results = await process.run(input_string)
        return results

async def main():
    tool1 = Tool("UPPER", "Converts text to uppercase", lambda text: text.upper())
    task1 = Task("id_1", "hello", lambda _: asyncio.sleep(2, "hello (async)"), [tool1], critical=True)
    task1.set_tool_limit(tool1.name, 2)

    task2 = Task("id_2", "world", lambda _: asyncio.sleep(2, "world (async)"))

    task3 = Task("id_3", "concatenate", lambda x: asyncio.sleep(2, x + " concatenated (async)"), [tool1])
    task3.set_tool_limit(tool1.name, 1)

    print("Running tasks in parallel:")
    my_process = CustomProcess("Parallel Process", [task1, task2], True, lambda x: x.upper())
    agent = Agent()
    results = await agent.execute_process(my_process, "hello world")
    print("Results:", [result for result in results if not isinstance(result, Exception)])
    print("Execution history:", " ".join(my_process.get_execution_history()))
    print("Failures:", "\n".join(my_process.get_failures()))

    print("\nRunning tasks sequentially:")
    my_process = CustomProcess("Sequential Process", entrypoint=lambda x: x.lower())
    my_process.add_task(task1,3)
    my_process.add_task(task2)
    my_process.add_task(task3)
    my_process.is_parallel = False
    results2 = await agent.execute_process(my_process, "HELLO WORLD")
    print("Results:", [result for result in results2 if not isinstance(result, Exception)])
    print("Execution history:", " ".join(my_process.get_execution_history()))
    print("Failures:", "\n".join(my_process.get_failures()))

asyncio.run(main())
