import asyncio

class Tool:
    def __init__(self, name, operation):
        self.name = name
        self.operation = operation
        self.usage_count = 0

    def run(self, input):
        return self.operation(input)

class Task:
    def __init__(self, task_id, description, run_function, tools=None):
        if tools is None:
            tools = []
        self.task_id = task_id
        self.description = description
        self.run_function = run_function
        self.tools = tools
        self.tool_limits = {}

    async def use_tool(self, tool_name, input):
        tool = next((tool for tool in self.tools if tool.name == tool_name), None)
        if not tool:
            raise Exception(f"No tool found with name: {tool_name}")
        if tool_name in self.tool_limits and self.tool_limits[tool_name] <= tool.usage_count:
            raise Exception(f"Usage limit exceeded for tool: {tool.name} in task: {self.description}")
        tool.usage_count += 1
        return tool.run(input)

    async def execute(self):
        print(f"Starting task: {self.description}")
        result = await self.run_function()
        for tool in self.tools:
            result = await self.use_tool(tool.name, result)
        print(f"Finished task: {self.description}")
        return result

    def set_tool_limit(self, tool_name, limit):
        self.tool_limits[tool_name] = limit

class CustomProcess:
    def __init__(self, tasks=None, is_parallel=False):
        if tasks is None:
            tasks = []
        self.tasks = tasks
        self.is_parallel = is_parallel
        self.execution_history = []

    async def run(self):
        results = []
        if self.is_parallel:
            print("Running tasks in parallel...")
            tasks = [task.execute() for task in self.tasks]
            results = await asyncio.gather(*tasks)
        else:
            print("Running tasks sequentially...")
            for task in self.tasks:
                try:
                    result = await task.execute()
                    results.append(result)
                    self.execution_history.append(f"Task executed: {task.description}")
                except Exception as error:
                    print(f"Error executing task: {task.description}", error)
        return results

    def add_task(self, task, repetitions=1):
        for _ in range(repetitions):
            self.tasks.append(task)

    def clear_tasks(self):
        self.tasks = []
        self.execution_history = []

    def get_execution_history(self):
        return self.execution_history.copy()

class Agent:
    def __init__(self):
        pass

    async def execute_process(self, process):
        return await process.run()

async def main():
    tool1 = Tool("UPPER", lambda text: text.upper())
    task1 = Task("id_1", "hello", lambda: asyncio.sleep(2, "hello (async)"), [tool1])
    task1.set_tool_limit(tool1.name, 3)

    task2 = Task("id_2", "world", lambda: asyncio.sleep(2, "world (async)"))

    print("Running tasks in parallel:")
    my_process = CustomProcess([task1, task2], True)
    agent = Agent()
    results = await agent.execute_process(my_process)
    print("Results:", results)
    print("Execution history:", " ".join(my_process.get_execution_history()))

    print("\nRunning tasks sequentially:")
    my_process.clear_tasks()
    my_process.add_task(task1, 3)
    my_process.add_task(task2)
    my_process.is_parallel = False
    results2 = await agent.execute_process(my_process)
    print("Results:", results2)
    print("Execution history:", " ".join(my_process.get_execution_history()))

asyncio.run(main())
