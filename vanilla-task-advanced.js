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
      console.log(`Starting task: ${this.description}`);
      let result = await this.runFunction();
      for (const tool of this.tools) {
        result = this.useTool(tool.name, result);
      }
      console.log(`Finished task: ${this.description}`);
      return result;
    }
  
    setToolLimit(toolName, limit) {
      this.toolLimits[toolName] = limit;
    }
  }
  
  class CustomProcess {
    constructor(name, tasks = [], isParallel = false) {
      this.name = name;
      this.tasks = tasks;
      this.isParallel = isParallel;
      this.executionHistory = [];
      this.failures = [];
    }
  
    async run() {
      const results = [];
      console.log(`Running tasks ${this.isParallel ? 'in parallel' : 'sequentially'} in process: ${this.name}...`);
      if (this.isParallel) {
        const promises = this.tasks.map(task => this.executeTask(task));
        results.push(...await Promise.all(promises));
      } else {
        for (const task of this.tasks) {
          const result = await this.executeTask(task);
          results.push(result);
        }
      }
      return results;
    }
  
    async executeTask(task) {
      try {
        const result = await task.execute();
        this.executionHistory.push(`Task executed: ${task.description}`);
        return result;
      } catch (error) {
        console.error(`Error executing task: ${task.description} in process: ${this.name}`, error);
        this.failures.push(`Failure in process ${this.name}: ${error.message}`);
        return error;
      }
    }
  
    addTask(task, repetitions = 1) {
      for (let i = 0; i < repetitions; i++) {
        this.tasks.push(task);
      }
    }
  
    clearTasks() {
      this.tasks = [];
      this.executionHistory = [];
      this.failures = [];
    }
  
    getExecutionHistory() {
      return [...this.executionHistory];
    }
  
    getFailures() {
      return [...this.failures];
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
    const task1 = new Task("id_1", "hello", () => new Promise(resolve => setTimeout(() => resolve("hello (async)"), 2000)), [tool1]);
    task1.setToolLimit(tool1.name, 3);
  
    const task2 = new Task("id_2", "world", () => new Promise(resolve => setTimeout(() => resolve("world (async)"), 2000)), []);
  
    console.log("Running tasks in parallel:");
    let myProcess = new CustomProcess("Parallel Process", [task1, task2], true);
    const agent = new Agent();
    let results = await agent.executeProcess(myProcess);
    console.log("Results:", results.filter(result => !(result instanceof Error)));
    console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
    console.log("Failures:", myProcess.getFailures().join("\n"));
  
    console.log("\nRunning tasks sequentially:");
    myProcess = new CustomProcess("Sequential Process");
    myProcess.addTask(task1, 3);
    myProcess.addTask(task2);
    myProcess.isParallel = false;
    results = await agent.executeProcess(myProcess);
    console.log("Results:", results.filter(result => !(result instanceof Error)));
    console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
    console.log("Failures:", myProcess.getFailures().join("\n"));
  }
  
  main();
