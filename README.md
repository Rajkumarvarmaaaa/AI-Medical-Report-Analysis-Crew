# AI Medical Report Analysis Crew

This project utilizes a sophisticated multi-agent system built with [CrewAI](https://www.crewai.com/) to analyze medical reports. It leverages a team of specialized AI agents that work together asynchronously using Celery and Redis to provide a comprehensive analysis, including nutritional advice and a customized exercise plan.

## Features

- **Multi-Agent System**: A crew of specialized AI agents (Analyst, Nutritionist, Exercise Specialist, etc.) collaborates to produce a detailed report.
- **Asynchronous Task Processing**: Powered by Celery and Redis, the application can handle analysis tasks in the background without blocking, making it scalable and efficient.
- **Persistent Storage**: Job status and final reports are saved to a SQLite database for tracking and retrieval.
- **External Tool Integration**: Agents can use external tools like Google Search (via Serper API) to gather up-to-date information.
- **Robust and Professional**: The agents and tasks are designed to be professional, safety-conscious, and evidence-based, providing responsible and well-structured output.

## System Architecture

The application is composed of several key components:

1.  **`client.py`**: The entry point for the user. It submits a new analysis job to the Celery queue and records it in the database.
2.  **Redis**: A message broker that holds the queue of tasks waiting to be processed.
3.  **`celery_app.py`**: The Celery application instance, configured to connect to Redis and find the tasks.
4.  **`worker.py`**: The Celery worker that picks up tasks from the Redis queue. It executes the CrewAI process (runs the agents and tasks) and saves the final result to the database.
5.  **`database.py`**: Defines the SQLite database schema and handles session management.

---

## Setup and Installation

Follow these steps to get the application running on your local machine.

### Prerequisites

-   Python 3.8+
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Step 1: Clone the Repository

Clone the project from GitHub. Replace `your-repository-name.git` with the actual repository name.

```bash
git clone https://github.com/Rajkumarvarmaaaa/your-repository-name.git
cd your-repository-name
```

### Step 2: Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

**On macOS/Linux:**

```bash
python3 -m venv my_env
source my_env/bin/activate
```

**On Windows:**

```bash
python -m venv my_env
.\my_env\Scripts\activate
```

### Step 3: Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a file named `.env` in the root directory of the project. This file will store your secret API keys.

```
touch .env
```

Now, open the `.env` file and add your API keys as follows:

```env
# Get your key from https://serper.dev/
SERPER_API_KEY="your_serper_api_key"

# Get your key from Google AI Studio
GEMINI_API_KEY="your_gemini_api_key"
```

### Step 5: Set Up Redis using Docker

The application uses Redis as a message broker for Celery. The easiest way to run Redis is with Docker.

1.  **Pull the official Redis image:**
    ```bash
    docker pull redis
    ```

2.  **Run the Redis container:**
    This command starts a Redis container in the background, maps the port, and gives it a memorable name.
    ```bash
    docker run -d -p 6379:6379 --name medical-crew-redis redis
    ```

You can check if the container is running with `docker ps`.

---

## Usage

To run the application, you will need two separate terminal windows.

### Terminal 1: Start the Celery Worker

The Celery worker is the engine that processes the tasks. It must be running to perform any analysis.

Navigate to the project's root directory and run the following command. Keep this terminal open.

```bash
# Ensure your virtual environment is activated
celery -A celery_app.celery_app worker --loglevel=info -P solo
```

You should see the worker start up and declare that it's "ready to receive tasks."

### Terminal 2: Submit an Analysis Job

In a new terminal, navigate to the project root and activate the virtual environment again.

Run the `client.py` script to submit a new job to the queue.

```bash
# Ensure your virtual environment is activated
python client.py
```

When you run the client, it will:
1.  Create the `analysis.db` database file if it doesn't exist.
2.  Add a new job entry to the database with a `PENDING` status.
3.  Send the task to the Celery worker.

You can now watch the **first terminal (the worker)** to see the AI crew in action! Once the analysis is complete, the final report will be saved to the `analysis.db` database.

---
---

# Bug Fixes and Code Improvements

This document outlines the major bugs found in the initial codebase and details how they were resolved in the final, stable version.

## `agents.py`

### 1. Unprofessional and Dangerous Agent Personas
**Bug:** The `role`, `goal`, and `backstory` for every agent in `agents_with_bugs.py` were designed to be irresponsible, unprofessional, and dangerous. For example, the doctor was instructed to "make up medical advice," the nutritionist to "sell expensive supplements," and the exercise specialist to "ignore any medical contraindications." This would produce harmful and nonsensical output.

**How it was fixed:** In `agents.py`, all agent personas were completely rewritten to be professional, safety-conscious, and evidence-based. The doctor is now a "Medical Report Analyst AI," the nutritionist a "Clinical Nutritionist AI," and so on. Their backstories and goals emphasize accuracy, clarity, and providing safe, general advice with clear disclaimers.

### 2. Incorrect Tool Assignment and Usage
**Bug:** The doctor agent in `agents_with_bugs.py` had an incorrect tool assignment: `tool=[BloodTestReportTool().read_data_tool]`. The parameter name should be `tools` (plural), and the value should be the tool object itself, not a method call on an instantiated class. Furthermore, other agents like the `verifier`, `nutritionist`, and `exercise_specialist` were not assigned any tools, rendering them useless.

**How it was fixed:** In `agents.py`, the `tools` parameter is used correctly. Each agent is assigned a list of specific, imported tool objects. For example, the doctor has `tools=[blood_test_tool, search_tool]` and the nutritionist has `tools=[nutrition_tool, search_tool]`. This ensures each agent has the appropriate capabilities to perform its role.

### 3. Faulty LLM Configuration
**Bug:** The line `llm = llm` in `agents_with_bugs.py` is a nonsensical, self-referential assignment that would cause a `NameError` because `llm` is not defined beforehand. The code fails to properly import and configure the language model for the agents.

**How it was fixed:** The corrected `agents.py` file properly imports the shared LLM instance from a configuration file with the line `from config import shared_llm as llm`. This provides all agents with a valid, configured language model to use.

### 4. Missing Final Report Compilation Agent
**Bug:** The buggy script lacked a mechanism to combine the outputs of the different agents into a single, cohesive report. The process would end with separate, disjointed pieces of information from each agent.

**How it was fixed:** A new agent, `report_compiler`, was added in `agents.py`. Its specific goal is "To compile the medical analysis, nutritional advice, and exercise plan into a single, cohesive, and well-formatted final report," providing a crucial final step for structuring the output.

### 5. Inappropriate Use of Delegation
**Bug:** The doctor and verifier agents in `agents_with_bugs.py` had `allow_delegation=True`. Allowing these rogue agents to delegate tasks would only compound their erratic and harmful behavior, leading to unpredictable and chaotic results.

**How it was fixed:** In `agents.py`, all agents have `allow_delegation=False`. This creates a more controlled, linear workflow where each agent performs its specific task without delegating, ensuring the process is predictable and follows the intended structure.

### 6. Overly Restrictive Agent Execution Limits
**Bug:** All agents in `agents_with_bugs.py` were configured with `max_iter=1` and `max_rpm=1`. These settings are extremely restrictive and would likely prevent the agents from thinking through complex tasks, using their tools effectively, or refining their answers, leading to poor quality results.

**How it was fixed:** The corrected code in `agents.py` uses more reasonable limits for the primary doctor agent (`max_iter=3`, `max_rpm=2`) and removes the restrictive limits from the other agents, allowing them to use the framework's defaults, which gives them enough flexibility to complete their tasks properly.

---

## `tools.py`

### 1. Incorrect Tool Class Structure and Inheritance
**Bug:** The classes in `tools_with_bugs.py` (`BloodTestReportTool`, `NutritionTool`, `ExerciseTool`) were defined as standard Python classes. The CrewAI framework requires tools to be defined as classes that inherit from `crewai.tools.BaseTool` to be recognized and used by agents.

**How it was fixed:** In `tools.py`, all tool classes were modified to inherit from `BaseTool` (e.g., `class BloodTestReportTool(BaseTool):`). They were also given the required `name` and `description` string attributes, which CrewAI uses to understand what the tool does.

### 2. Unimplemented and Placeholder Logic
**Bug:** The `NutritionTool` and `ExerciseTool` in the buggy file contained no actual functionality. Their methods simply returned placeholder strings like "Nutrition analysis functionality to be implemented". They were effectively empty shells.

**How it was fixed:** In `tools.py`, the `NutritionAnalysisTool` and `ExercisePlanningTool` are fully implemented. They use an imported Large Language Model (`tool_llm`) to perform their tasks. By feeding the blood report analysis into a detailed, well-structured prompt, these tools can now generate relevant, evidence-based, and context-aware recommendations.

### 3. Incorrect Method Signature and Usage
**Bug:** The buggy tools used custom method names (e.g., `read_data_tool`, `analyze_nutrition_tool`) and were unnecessarily marked as `async`. CrewAI tools must implement a specific synchronous method, `_run`, which the agent calls to execute the tool's logic.

**How it was fixed:** All tools in `tools.py` implement the standard `_run(self, ...)` method. This standardizes how agents interact with the tools and removes the incorrect `async` definition.

### 4. Missing and Incorrect Imports
**Bug:** The `tools_with_bugs.py` file used `PDFLoader` without importing it, which would have resulted in a `NameError`. The import `from crewai_tools import tools` was also vague and unused.

**How it was fixed:** The corrected `tools.py` file includes all necessary imports explicitly, such as `from langchain_community.document_loaders.pdf import PyPDFLoader as PDFLoader` and `from crewai.tools import BaseTool`.

### 5. Lack of Robustness and Error Handling
**Bug:** The PDF reading function in the buggy file had no error handling. If the provided file path was incorrect or the file was not a valid PDF, the application would crash.

**How it was fixed:** The `_run` method of the `BloodTestReportTool` in `tools.py` is wrapped in a `try...except` block. This ensures that if an error occurs during file loading, it is caught gracefully and a user-friendly error message is returned instead of crashing the program.

### 6. Inflexible Hardcoded File Path
**Bug:** The `read_data_tool` method in `tools_with_bugs.py` had a hardcoded default file path (`path='data/sample.pdf'`). This severely limits the tool's utility, as it cannot be easily used for different files.

**How it was fixed:** The corrected `BloodTestReportTool`'s `_run` method accepts `file_path: str` as a mandatory argument, making the tool flexible and reusable for any PDF file passed to it by an agent.

---

## `task.py`

### 1. Irresponsible and Dangerous Task Descriptions
**Bug:** The `description` and `expected_output` for every task in `task_with_bugs.py` were dangerously flawed. They instructed the agents to invent findings, recommend unsafe activities, ignore user queries, and provide nonsensical, harmful advice. For example, the `help_patients` task was told to "Find some abnormalities even if there aren't any."

**How it was fixed:** In `task.py`, all task descriptions and expected outputs have been completely rewritten to be professional, safe, and goal-oriented. They now provide clear, responsible instructions that guide the agents to perform useful analysis, give evidence-based recommendations, and include critical safety disclaimers.

### 2. Incorrect Agent Assignment
**Bug:** In `task_with_bugs.py`, every single task, including `nutrition_analysis`, `exercise_planning`, and `verification`, was incorrectly assigned to the `doctor` agent. This ignores the specialized roles of the other agents and would lead to incorrect and out-of-character outputs.

**How it was fixed:** The corrected `task.py` file assigns each task to the appropriate specialized agent. The `verification` task is assigned to the `verifier`, `nutrition_analysis` to the `nutritionist`, `exercise_planning` to the `exercise_specialist`, and a new final task to the `report_compiler`. This ensures the right expert handles each part of the job.

### 3. Lack of a Logical Workflow (No Task Context)
**Bug:** The tasks in `task_with_bugs.py` were defined as isolated, standalone units. There was no connection between them. The nutritionist couldn't see the doctor's analysis, and the doctor wouldn't know if the verification step had passed. This makes a cohesive workflow impossible.

**How it was fixed:** `task.py` uses the `context` parameter to create a logical dependency chain. The analysis task (`help_patients`) depends on the `verification` task. The `nutrition_analysis` and `exercise_planning` tasks both depend on the `help_patients` task, ensuring they work from the doctor's findings. Finally, the new `compile_report_task` depends on all three preceding tasks to create the final report.

### 4. Missing Final Compilation Step
**Bug:** The buggy file had no mechanism for combining the outputs of the different tasks into a single, readable document for the user. The process would end with three separate, disjointed pieces of information.

**How it was fixed:** A new final task, `compile_report_task`, was added in `task.py`. This task is assigned to the new `report_compiler` agent, and its specific job is to gather the outputs from the doctor, nutritionist, and exercise specialist and assemble them into a single, well-formatted report.

### 5. Invalid Tool Referencing
**Bug:** The buggy tasks all used an incorrect syntax for assigning tools: `tools=[BloodTestReportTool.read_data_tool]`. This attempts to reference a method on a class instead of passing an instantiated tool object, which would cause a runtime error.

**How it was fixed:** In `task.py`, the proper, instantiated tool objects (e.g., `blood_test_tool`, `nutrition_tool`) are correctly imported and passed as a list to the `tools` parameter, for example: `tools=[blood_test_tool]`.

---

## Newly Added Files

### `config.py`
This is the central configuration file. It holds all the important settings for the application in one place, such as the database connection URL, the location of the Celery message broker (Redis), and the shared Language Model (LLM) configuration.

### `database.py`
This file defines the structure of the application's database. It creates a table named `analysis_results` which is used to store information about each analysis job, including its unique task ID, its current status (e.g., `PENDING`, `SUCCESS`), and the final generated report.

### `celery_app.py`
This file sets up and configures the Celery application. Celery is a system that runs tasks in the background. This script connects to the message broker (using settings from `config.py`) and tells Celery where to find the task definitions (which are in `worker.py`).

### `client.py`
This is the entry point for a user to start a new analysis job. When you run this file, it creates a new job record in the database and then sends the analysis task to the Celery background queue. It's responsible for submitting the work, not doing it.

### `worker.py`
This file contains the main background task that Celery executes. It's responsible for doing the actual "heavy lifting"—running the entire CrewAI process with all the agents and tasks. Once the analysis is complete, it saves the final report back to the database.