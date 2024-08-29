class Task {
    constructor(description) {
      this.description = description;
    }
  
    async run() {
      return this.description;
    }
  }
  
  class CustomProcess {
    constructor(tasks = []) {
      this.tasks = tasks;
      this.executionHistory = [];
    }
  
    async run() {
      const results = [];
      for (const task of this.tasks) {
        const result = await task.run();
        results.push(result);
        this.executionHistory.push(task.description);
        console.log(`Task executed: ${task.description}`);
      }
      return results;
    }
  
    add_task(task, repetitions = 1) {
      for (let i = 0; i < repetitions; i++) {
        this.tasks.push(task);
      }
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
    const myProcess = new CustomProcess([task2]);
    myProcess.add_task(task1, 2);  // Add task1 twice
    myProcess.add_task(task2);
    const agent = new Agent();
    const results = await agent.executeProcess(myProcess);
    console.log("Execution history:", myProcess.executionHistory.join(" "));
  }
  main();
