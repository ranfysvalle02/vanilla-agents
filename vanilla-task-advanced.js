class Tool {
    constructor(name, operation) {
      this.name = name;
      this.operation = operation;
      this.usageCount = 0;
    }
  
    run(input) {
      return this.operation(input);
    }
  }
  
  class Task {
    constructor(taskId, description, runFunction, tools = []) {
      this.taskId = taskId;
      this.description = description;
      this.runFunction = runFunction;
      this.tools = tools;
      this.toolLimits = {};
    }
  
    useTool(toolName, input) {
      const tool = this.tools.find((tool) => tool.name === toolName);
      if (!tool) {
        throw new Error(`No tool found with name: ${toolName}`);
      }
      if (this.toolLimits[toolName] && this.toolLimits[toolName] <= tool.usageCount) {
        throw new Error(`Usage limit exceeded for tool: ${tool.name} in task: ${this.description}`);
      }
      tool.usageCount++;
      return tool.run(input);
    }
  
    async execute() {
      let result = await this.runFunction();
      for (const tool of this.tools) {
        result = this.useTool(tool.name, result);
      }
      return result;
    }
  
    setToolLimit(toolName, limit) {
      this.toolLimits[toolName] = limit;
    }
  }
  
  class CustomProcess {
    constructor(tasks = [], isParallel = false) {
      this.tasks = tasks;
      this.isParallel = isParallel;
      this.executionHistory = [];
    }
  
    async run() {
      const results = [];
      if (this.isParallel) {
        const promises = this.tasks.map(task => task.execute().then(result => {
          this.executionHistory.push(`Task executed: ${task.description}`);
          console.log(`Task executed: ${task.description}`);
          return result;
        }).catch(error => {
          console.error(`Error executing task: ${task.description}`, error);
        }));
        results.push(...await Promise.all(promises));
      } else {
        for (const task of this.tasks) {
          try {
            const result = await task.execute();
            results.push(result);
            this.executionHistory.push(`Task executed: ${task.description}`);
            console.log(`Task executed: ${task.description}`);
          } catch (error) {
            console.error(`Error executing task: ${task.description}`, error);
          }
        }
      }
      return results;
    }
  
    add_task(task, repetitions = 1) {
      for (let i = 0; i < repetitions; i++) {
        this.tasks.push(task);
      }
    }
  
    clear_tasks() {
      this.tasks = [];
      this.executionHistory = [];
    }
  
    getExecutionHistory() {
      return this.executionHistory.slice();
    }
  }
  
  class Agent {
    constructor() {}
  
    async executeProcess(process) {
      return process.run();
    }
  }
  
  async function main() {
    const tool1 = new Tool("UPPER", (text) => text.toUpperCase());
    const task1 = new Task("id_1", "hello", async () => {
      const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
      await delay(2000);
      return "hello (async)";
    }, [tool1]);
    task1.setToolLimit(tool1.name, 3);
  
    const task2 = new Task("id_2", "world", async () => {
      const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
      await delay(2000);
      return "world (async)";
    }, []);
  
    console.log("Running tasks in parallel:");
    const myProcess = new CustomProcess([task1, task2], true);
    const agent = new Agent();
    const results = await agent.executeProcess(myProcess);
    console.log("Results:", results);
    console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
  
    console.log("\nRunning tasks sequentially:");
    myProcess.clear_tasks();
    myProcess.add_task(task1, 3);
    myProcess.add_task(task2);
    myProcess.isParallel = false;
    const results2 = await agent.executeProcess(myProcess);
    console.log("Results:", results2);
    console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
    
    console.log("\nRunning tasks sequentially with increased tool limits:");
    myProcess.clear_tasks();
    task1.setToolLimit(tool1.name, 10);
    myProcess.add_task(task1, 3);
    myProcess.add_task(task2);
    const results3 = await agent.executeProcess(myProcess);
    console.log("Results:", results3);
    console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
  }
  
  main();
