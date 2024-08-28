class Task:
    def __init__(self, description):
        self.description = description

    async def run(self):
        return self.description

class CustomProcess:
    def __init__(self, tasks):
        self.tasks = tasks

    async def run(self):
        results = []
        for task in self.tasks:
            result = await task.run()
            results.append(result)
        return results

class Agent:
    def __init__(self):
        pass

    async def execute_process(self, process):
        return await process.run()

async def main():
    task1 = Task("Hello")
    task2 = Task("world")

    my_process = CustomProcess([task1, task2])
    agent = Agent()

    results = await agent.execute_process(my_process)
    print(" ".join(results))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
