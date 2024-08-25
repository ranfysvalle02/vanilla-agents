## A Lightweight, Customizable AI Agent Framework

**Introducing `vanilla-agents`**

In the realm of conversational AI, having a robust and flexible framework is essential. `vanilla-agents` provides just that, offering a lightweight and customizable implementation that empowers you to leverage the capabilities of your preferred LLM provider without the need for additional, often bloated libraries.

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
