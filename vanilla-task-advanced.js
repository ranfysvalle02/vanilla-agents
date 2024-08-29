class Tool {
    constructor(name, operation) {
      this.name = name;
      this.operation = operation;
      this.usageCount = 0; // Initialize usageCount
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
      this.toolLimits = {}; // Initialize toolLimits here
    }
  
    useTool(toolName, input) {
      const tool = this.tools.find((tool) => tool.name === toolName);
      if (!tool) {
        throw new Error(`No tool found with name: ${toolName}`);
      }
      tool.usageCount++; // Increment usageCount before checking limit
      if (this.toolLimits[toolName] && this.toolLimits[toolName] < tool.usageCount) {
        throw new Error(`Usage limit exceeded for tool: ${tool.name} in task: ${this.description}`);
      }
      return tool.run(input); // Return the result of the tool's operation
    }
  
    async execute() {
      let result = await this.runFunction();
      for (const tool of this.tools) {
        result = this.useTool(tool.name, result); // Pass the result to the tool
      }
      return result; // Return the final result
    }
  
    setToolLimit(toolName, limit) {
      this.toolLimits[toolName] = limit;
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
        try {
          const result = await task.execute();
          results.push(result);
          this.executionHistory.push(`Task executed: ${task.description}`);
          console.log(`Task executed: ${task.description}`);
        } catch (error) {
          console.error(`Error executing task: ${task.description}`, error);
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
      return this.executionHistory.slice(); // Return a copy of the array
    }
  }
  
  class Agent {
    constructor() {}
  
    async executeProcess(process) {
      return process.run();
    }
  }
  
  async function main() {
    // Create a Tool instance
    const tool1 = new Tool("UPPER", (text) => text.toUpperCase());
  
    // Create a Task instance with a taskId, a function for run, and a set of tools
    const task1 = new Task("id_1", "hello", () => "hello (sync)", [tool1]);
    task1.setToolLimit(tool1.name, 3); // Set limit for tool1 in task1
  
    const task2 = new Task("id_2", "world", async () => {
      // Simulate an async operation
      const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
      await delay(1000);
      return "world (async)";
    }, []);
  
    const myProcess = new CustomProcess();
    myProcess.add_task(task1,4);
    myProcess.add_task(task2);
  
    const agent = new Agent();
    const results = await agent.executeProcess(myProcess);
    console.log("Results:", results);
  
    console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
  }
  
  main();
