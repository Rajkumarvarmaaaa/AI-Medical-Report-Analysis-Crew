# Importing libraries and files
from crewai import Task
# MODIFIED: Import all agents and tools
from agents import doctor, verifier, nutritionist, exercise_specialist, report_compiler
from tools import blood_test_tool, nutrition_tool, exercise_tool

# Task 1: Verification
verification = Task(
    description="Verify that the file at {file_path} appears to be a medical document, like a blood report. "
                "Scan the document for common medical terms, tables, and reference ranges. "
                "State whether the document is suitable for medical analysis.",
    expected_output="A confirmation statement. For example: 'The document at {file_path} has been verified and "
                    "appears to be a blood test report suitable for analysis.' or 'The document does not "
                    "appear to be a standard medical report.'",
    agent=verifier,
    tools=[blood_test_tool],
    async_execution=False
)

# Task 2: Main Analysis
help_patients = Task(
    description="Analyze the blood test report from this file: {file_path}.\n"
                "First, read the content of the file using the Blood Test Report Reader tool.\n"
                "Then, provide a summary of the key findings based on the user's query: {query}.\n"
                "Identify any biomarkers that are outside of the standard reference ranges and explain what they typically measure.\n"
                "Conclude with a clear disclaimer that this is an AI-generated analysis and not a substitute for professional medical advice.",
    expected_output="""A clear, structured summary of the blood test report. The output should be in Markdown format and include:
- A brief introduction addressing the user's query.
- A section titled 'Key Findings' with a bulleted list of important biomarkers from the report, their values, and their standard ranges.
- A section titled 'Analysis' highlighting any values that are high or low, with a brief, neutral explanation of what these markers generally relate to.
- A concluding paragraph with a strong disclaimer urging the user to consult a qualified healthcare professional for a proper diagnosis and treatment plan.""",
    agent=doctor,
    tools=[blood_test_tool],
    async_execution=False,
    # MODIFIED: Make this task dependent on the verification task
    context=[verification]
)

# Task 3: Nutrition Advice
nutrition_analysis = Task(
    description="Based on the medical report analysis provided in the context, provide general nutrition advice. "
                "Focus on well-established links between biomarkers and diet. Do not recommend specific supplements "
                "unless they are widely recognized (e.g., iron for anemia).",
    expected_output="""A list of general, evidence-based nutritional suggestions.
- Connect dietary advice to specific findings in the report (e.g., 'For elevated cholesterol, consider increasing soluble fiber...').
- Recommend food groups and healthy eating patterns rather than specific, restrictive diets.
- Include a disclaimer that this is not a personalized meal plan and a registered dietitian or doctor should be consulted.""",
    # MODIFIED: Assign to the correct agent and add context
    agent=nutritionist,
    tools=[nutrition_tool],
    context=[help_patients],
    async_execution=False,
)

# Task 4: Exercise Plan
exercise_planning = Task(
    description="Based on the medical report analysis provided in the context, create a general exercise plan. "
                "The plan should be safe and suitable for a general audience. "
                "Do not suggest overly strenuous or high-risk activities.",
    expected_output="""A sample weekly exercise plan.
- Include a mix of cardiovascular, strength, and flexibility exercises.
- Specify recommended frequencies and durations (e.g., '30 minutes of moderate cardio, 3-5 times a week').
- Emphasize the importance of a warm-up and cool-down.
- Include a prominent safety warning to consult a doctor before beginning any new exercise regimen.""",
    # MODIFIED: Assign to the correct agent and add context
    agent=exercise_specialist,
    tools=[exercise_tool],
    context=[help_patients],
    async_execution=False,
)

# ADDED: Task 5: Final Report Compilation
compile_report_task = Task(
    description="Compile the analysis from the doctor, the nutritional advice, and the exercise plan into a single, cohesive report. "
                "The final output should be a well-structured Markdown document that is easy for the user to read. "
                "Ensure all necessary disclaimers from the previous tasks are included and prominently displayed.",
    expected_output="""A single, comprehensive Markdown document containing:
1.  **Blood Test Analysis:** The full analysis from the doctor.
2.  **Nutritional Recommendations:** The full advice from the nutritionist.
3.  **Exercise Recommendations:** The full plan from the fitness planner.
4.  **Final Disclaimers:** A consolidated and clear section of all disclaimers.
The report should be formatted professionally and be ready to be presented to the user.""",
    agent=report_compiler,
    context=[help_patients, nutrition_analysis, exercise_planning],
    async_execution=False,
)