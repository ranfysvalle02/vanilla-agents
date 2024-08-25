## Building an Advanced AI Agent with OpenAI, MongoDB, and DuckDuckGo

![](https://upload.wikimedia.org/wikipedia/commons/a/aa/AI_Agent_Overview.png)

**Introducing `vanilla-agents`**

**User Input -> Start Process -> Task Execution -> Tool Selection -> Complete Process -> Response Generation**

`vanilla-agents` provides a lightweight and customizable implementation that empowers you to leverage the capabilities of your preferred LLM provider without the need for additional, often bloated libraries. 

With just a few well-placed lines of code, you can take control and build a custom AI agent that bends to your will and can implement custom processes/workflows. 

## Breaking Down the Tasks into a Custom Process

* **Task 1: Search for YouTube Videos**
  * This task involves identifying relevant YouTube videos based on a given query or topic.
* **Task 2: Summarize the Content**
  * This task requires extracting the key points and ideas from the videos found in Task 1.

**Creating a Custom Process:**

To combine these tasks into a cohesive workflow, we can define a `CustomProcess` that:

1. **Retrieves Videos:** Uses a `YouTubeSearchTool` to search for videos based on a user-provided query.
2. **Extracts Content:** Employs a `YouTubeTranscriptTool` to extract the transcripts of the retrieved videos.
3. **Summarizes Content:** Utilizes a `TextSummarizationTool` to generate summaries from the extracted transcripts.

**Key Components and How They Work:**

1. **Tools:** These are the building blocks of your AI's functionality. Think of them as specialized skills. For instance, a `SearchTool` might leverage DuckDuckGo to retrieve information from the web.
2. **Tasks:** These are the specific actions your AI can perform. A task might involve using multiple tools in sequence. For example, a "Summarize" task could use a `SearchTool` to gather information and then employ a summarization technique.
3. **AdvancedAgent:** This is the core component that orchestrates the tools and tasks. It's responsible for understanding user prompts, selecting appropriate tools, and managing the conversation history.
4. **CustomProcess:** This allows you to chain tasks together, creating more complex workflows. For instance, you could define a process that first searches for information and then analyzes it using sentiment analysis.

**The Benefits of a Lightweight Approach:**

* **Flexibility:** You have full control over the components and their interactions. This allows you to tailor the AI to your specific needs.
* **Efficiency:** By avoiding unnecessary dependencies, you can maintain a lean and efficient implementation.
* **Customization:** You can easily add or remove tools and tasks as required, making the AI highly adaptable.
* **Control:** You have direct access to the code, enabling you to fine-tune behavior and troubleshoot issues.

**How It Works:**

1. **User Input:** The user provides a prompt or question.
2. **Tool Selection:** The `AdvancedAgent` analyzes the prompt and determines the most suitable tools to use.
3. **Task Execution:** The selected tools are employed to carry out the necessary tasks.
4. **Response Generation:** The `AdvancedAgent` combines the results from the tools and generates a response.

**The Foundation: Setting Up the Environment**

Our first step is to set up our environment. This involves importing necessary libraries and defining some constants. We're using libraries like `openai` for AI model interaction, `pymongo` for database management, `duckduckgo_search` for web search, and `youtube_transcript_api` for fetching YouTube video transcripts.

**The Memory: Conversation History Management**

As our AI assistant interacts with users, it's crucial to remember past conversations. We create a `ConversationHistory` class to manage this memory, storing it either in a local list or a MongoDB database for more persistent storage.

**The Skills: Tools and Tasks**

Our AI assistant needs skills to perform tasks. We represent these skills as `Tool` objects. For instance, we have a `SearchTool` that uses the DuckDuckGo search engine to retrieve information from the web. 

**The Actions: Tasks**

Tasks are the actions that our AI assistant can perform using its skills. For example, a task could be to search for information on a specific topic and summarize the findings. Each task is represented as an instance of the `Task` class, which includes a description of the task, the agent that will perform the task, the tools that the agent will use, and the input that the task will process.

**The Brain: Advanced Agent and Custom Process**

The `AdvancedAgent` is the brain of our AI assistant. It orchestrates the use of tools and tasks, generates responses to user prompts, and maintains the conversation history. 

**The Workflow: Custom Process**

Sometimes, our AI assistant needs to perform a series of tasks in a specific order. That's where the `CustomProcess` class comes in. It allows us to chain tasks together to create more complex workflows. For instance, we might have a process that involves searching for information, analyzing the results, and then summarizing the findings.

**The Adventure: Running the AI Assistant**

With all the components in place, it's time to set our AI assistant in motion. We create tasks, chain them into a process, and set the process running. As the tasks are performed, our AI assistant interacts with the user, remembers the conversation, and uses its tools to generate responses.


## **`response_format={"type": "json_object"}`**

By structuring responses in JSON format, you're essentially providing a blueprint for how the AI's thoughts can be interpreted and processed. The use of `response_format={"type": "json_object"}` when interacting with the OpenAI API is crucial for providing clear instructions to the AI model and receiving structured responses. Let's delve deeper into its significance and benefits.

## Conclusion

Now that you've seen the foundation for building your own AI agent, it's time to experiment! 
