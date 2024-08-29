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
  constructor(taskId, description, runFunction, tools = [], critical = false) {
      this.taskId = taskId;
      this.description = description;
      this.runFunction = runFunction;
      this.tools = tools;
      this.toolLimits = {};
      this.critical = critical;
  }

  async useTool(toolName, input) {
      const tool = this.tools.find(tool => tool.name === toolName);
      if (!tool) {
          throw new Error(`No tool found with name: ${toolName}`);
      }
      if (this.toolLimits[toolName] && this.toolLimits[toolName] <= tool.usageCount) {
          throw new Error(`Usage limit exceeded for tool: ${tool.name} in task: ${this.description}`);
      }
      tool.usageCount += 1;
      return tool.run(input);
  }

  async execute(input = null) {
      console.log(`${new Date()} - Starting task: ${this.description}`);
      let result = await this.runFunction(input);
      for (const tool of this.tools) {
          result = await this.useTool(tool.name, result);
      }
      console.log(`${new Date()} - Finished task: ${this.description}`);
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
      console.log(`${new Date()} - Running tasks ${this.isParallel ? 'in parallel' : 'sequentially'} in process: ${this.name}...`);
      if (this.isParallel) {
          await Promise.all(this.tasks.map(task => this.executeTask(task))).then(res => results.push(...res));
      } else {
          let previousResult = null;
          for (const task of this.tasks) {
              const result = await this.executeTask(task, previousResult);
              if (result === null && task.critical) {
                  break;
              }
              results.push(result);
              previousResult = result;
          }
      }
      return results;
  }

  async executeTask(task, input = null) {
      try {
          const result = await task.execute(input);
          this.executionHistory.push(`Task executed: ${task.description}`);
          return result;
      } catch (error) {
          console.error(`${new Date()} - Error executing task: ${task.description} in process: ${this.name}`, error);
          this.failures.push(`Failure in process ${this.name}: ${error}`);
          if (task.critical) {
              console.error(`${new Date()} - Critical task failed. Exiting process: ${this.name}`);
              return null;
          }
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
  async executeProcess(process) {
      const results = await process.run();
      return results;
  }
}

(async function main() {
  const tool1 = new Tool("UPPER", text => text.toUpperCase());
  const task1 = new Task("id_1", "hello", async () => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      return "hello (async)";
  }, [tool1], true);
  task1.setToolLimit(tool1.name, 2);

  const task2 = new Task("id_2", "world", async () => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      return "world (async)";
  });

  const task3 = new Task("id_3", "concatenate", async x => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      return `${x} concatenated (async)`;
  }, [tool1]);
  task3.setToolLimit(tool1.name, 1);

  console.log("Running tasks in parallel:");
  const myProcess = new CustomProcess("Parallel Process", [task1, task2], true);
  const agent = new Agent();
  let results = await agent.executeProcess(myProcess);
  console.log("Results:", results.filter(result => !(result instanceof Error)));
  console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
  console.log("Failures:", myProcess.getFailures().join("\n"));

  console.log("\nRunning tasks sequentially:");
  myProcess.clearTasks();
  myProcess.addTask(task1, 3);
  myProcess.addTask(task2);
  myProcess.addTask(task3);
  myProcess.isParallel = false;
  let results2 = await agent.executeProcess(myProcess);
  console.log("Results:", results2.filter(result => !(result instanceof Error)));
  console.log("Execution history:", myProcess.getExecutionHistory().join(" "));
  console.log("Failures:", myProcess.getFailures().join("\n"));
})();
