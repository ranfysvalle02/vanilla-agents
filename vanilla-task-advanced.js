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
      tool.usageCount++;
      if (this.toolLimits[toolName] && this.toolLimits[toolName] < tool.usageCount) {
        throw new Error(`Usage limit exceeded for tool: ${tool.name} in task: ${this.description}`);
      }
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
    constructor(tasks = [], parallel = false) {
      this.tasks = tasks;
      this.parallel = parallel;
      this.executionHistory = [];
    }
  
    async run() {
      const taskPromises = this.tasks.map((task) => this.executeTask(task));
      const results = this.parallel ? await Promise.all(taskPromises) : await this.sequentialExecution(taskPromises);
      return results;
    }
  
    async executeTask(task) {
      try {
        const result = await task.execute();
        this.executionHistory.push(`Task executed: ${task.description}`);
        console.log(`Task executed: ${task.description}`);
        return result;
      } catch (error) {
        console.error(`Error executing task: ${task.description}`, error);
      }
    }
  
    async sequentialExecution(taskPromises) {
      const results = [];
      for (const taskPromise of taskPromises) {
        results.push(await taskPromise);
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
  
    const task1 = new Task("id_1", "hello", () => "hello (sync)", [tool1]);
    task1.setToolLimit(tool1.name, 3);
  
    const task2 = new Task("id_2", "world", async () => {
      const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
      await delay(1000);
      return "world (async)";
    }, []);
  
    const myProcess = new CustomProcess([], true);
    myProcess.add_task(task1, 4);
    myProcess.add_task(task2);
  
    const agent = new Agent();
    const results = await agent.executeProcess(myProcess);
    console.log("Results:", results);
  
    console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
  }
  
  main();
