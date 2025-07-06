## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders.pdf import PyPDFLoader as PDFLoader
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from crewai import LLM # ADDED: To use an LLM within our tools
from config import shared_llm as tool_llm

# --- ADD THIS FOR DEBUGGING ---
print("--- DEBUGGING in tools.py ---")
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("SUCCESS: GEMINI_API_KEY found.")
else:
    print("ERROR: GEMINI_API_KEY not found in environment!")
print("--------------------------")
# --- END DEBUGGING SECTION ---

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class BloodTestReportTool(BaseTool):
    name: str = "Blood Test Report Reader"
    description: str = "Reads and extracts data from a blood test report PDF file."

    def _run(self, file_path: str):
        """Synchronous method to read PDF data."""
        try:
            docs = PDFLoader(file_path=file_path).load()
            full_report = ""
            for data in docs:
                content = data.page_content
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")
                full_report += content + "\n"
            return full_report
        except Exception as e:
            return f"Error reading PDF file: {e}. Please ensure the file path is correct and the file is a valid PDF."

blood_test_tool = BloodTestReportTool()

## Creating Nutrition Analysis Tool
# MODIFIED: Implemented the tool's logic using an LLM
class NutritionAnalysisTool(BaseTool):
    name: str = "Nutrition Recommender"
    description: str = "Provides general dietary recommendations based on an analysis of a blood report."

    def _run(self, blood_report_analysis: str) -> str:
        """Uses an LLM to generate nutrition recommendations from a report summary."""
        nutrition_prompt = f"""
        You are a specialized AI assistant acting as a clinical nutritionist.
        Your task is to generate general, evidence-based dietary recommendations based on the provided summary of a blood test report.

        - Connect your recommendations directly to the findings in the report (e.g., "Due to elevated LDL cholesterol, consider...").
        - Focus on food groups and healthy eating patterns, not restrictive or fad diets.
        - Do NOT invent or diagnose new conditions. Base your advice solely on the provided analysis.
        - Output the recommendations in Markdown format.
        - CRITICALLY: End with a clear and strong disclaimer that this is not personalized medical advice and the user must consult a registered dietitian or doctor.

        Here is the blood report analysis:
        ---
        {blood_report_analysis}
        ---

        Generate the nutritional recommendations now.
        """
        nutrician_response = tool_llm.call(nutrition_prompt)
        return nutrician_response

# Instantiate the tool
nutrition_tool = NutritionAnalysisTool()

## Creating Exercise Planning Tool
# MODIFIED: Implemented the tool's logic using an LLM
class ExercisePlanningTool(BaseTool):
    name: str = "Exercise Plan Creator"
    description: str = "Creates a general and safe exercise plan based on a health data summary."

    def _run(self, blood_report_analysis: str) -> str:
        """Uses an LLM to generate a safe exercise plan from a report summary."""
        excercise_prompt = f"""
        You are a specialized AI assistant acting as a certified fitness planner.
        Your task is to create a safe, general, and appropriate weekly exercise plan based on the provided summary of a health report.

        - The plan should be suitable for a general audience.
        - Consider any health flags in the analysis (e.g., if cholesterol is high, emphasize cardiovascular exercise).
        - Include a balanced mix of cardiovascular, strength, and flexibility exercises.
        - Specify recommended frequencies and durations (e.g., '3-5 times a week').
        - Emphasize the importance of warm-ups and cool-downs.
        - Do NOT suggest overly strenuous or high-risk activities.
        - Output the plan in Markdown format, structured as a sample weekly schedule.
        - CRITICALLY: End with a prominent safety disclaimer that this is a sample plan and the user must consult a doctor before beginning any new exercise regimen.

        Here is the health report analysis:
        ---
        {blood_report_analysis}
        ---

        Generate the exercise plan now.
        """
        excercise_response = tool_llm.call(excercise_prompt)
        return excercise_response

# Instantiate the tool
exercise_tool = ExercisePlanningTool()