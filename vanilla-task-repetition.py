class Task:
    def __init__(self, description):
        self.description = description

    async def run(self):
        return self.description

class CustomProcess:
    def __init__(self, tasks):
        self.tasks = tasks
        self.execution_history = []

    async def run(self):
        for task in self.tasks:
            result = await task.run()
            self.execution_history.append(task.description)
            print(f"Task executed: {task.description}")
        return self.execution_history

    def add_task(self, task, repetitions=1):
        """Adds a task to the process, repeating it if specified."""
        self.tasks.extend([task for _ in range(repetitions)])

class Agent:
    def __init__(self):
        pass

    async def execute_process(self, process):
        return await process.run()

async def main():
    task1 = Task("Task 1")
    task2 = Task("Task 2")

    my_process = CustomProcess([task2])
    my_process.add_task(task1, 2)  # Add task1 twice
    my_process.add_task(task2)

    agent = Agent()

    results = await agent.execute_process(my_process)
    print("Execution history:", results)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
