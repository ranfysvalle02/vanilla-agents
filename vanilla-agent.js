class Task {
    constructor(description) {
        this.description = description;
    }

    async run() {
        return this.description;
    }
}

class CustomProcess {
    constructor(tasks) {
        this.tasks = tasks;
    }

    async run() {
        const results = [];
        for (const task of this.tasks) {
            const result = await task.run();
            results.push(result);
        }
        return results;
    }
}

class Agent {
  constructor() {}

  async executeProcess(process) {
    return process.run();
  }
}

async function main() {
  const task1 = new Task("Hello");
  const task2 = new Task("world");

  const myProcess = new CustomProcess([task1, task2]);
  const agent = new Agent();

  const results = await agent.executeProcess(myProcess);
  console.log(results.join(" "));
}

main();
