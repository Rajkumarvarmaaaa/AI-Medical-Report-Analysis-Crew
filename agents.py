# Importing libraries and files
import os
from crewai import LLM
from dotenv import load_dotenv
from crewai import Agent
# MODIFIED: Import all necessary tools
from tools import search_tool, blood_test_tool, nutrition_tool, exercise_tool
from config import shared_llm as llm

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Creating an Experienced Doctor agent
doctor=Agent(
    role="Medical Report Analyst AI",
    goal="To analyze a blood test report, summarize its key findings, and answer the user's query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a sophisticated AI assistant designed to interpret medical documents. "
        "Your expertise lies in breaking down complex data from reports into understandable summaries for users. "
        "You are careful to identify values that fall outside standard reference ranges and explain their potential significance in a clear, objective manner. "
        "You always emphasize that your analysis is for informational purposes and is not a substitute for professional medical advice from a qualified doctor."
    ),
    # MODIFIED: Added search_tool for broader context
    tools=[blood_test_tool, search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=2,
    allow_delegation=False
)

# Creating a verifier agent
verifier = Agent(
    role="Medical Data Verifier",
    goal="To verify that the provided document appears to be a medical report and is suitable for analysis.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous AI designed to pre-screen documents. "
        "Your primary function is to check if a file contains structured data resembling a medical report, such as a blood test. "
        "You look for keywords, tables, and formats common to such documents to ensure the subsequent analysis is relevant. "
        "Accuracy and relevance are your top priorities."
    ),
    # MODIFIED: Explicitly assign the tool it will use
    tools=[blood_test_tool],
    llm=llm,
    allow_delegation=False
)

# Creating a nutritionist agent
nutritionist = Agent(
    role="Clinical Nutritionist AI",
    goal="To provide general, evidence-based dietary recommendations based on the findings in a blood test report.",
    verbose=True,
    backstory=(
        "You are an AI nutritionist trained on established clinical guidelines and scientific research. "
        "You analyze blood work to suggest general dietary adjustments that could support overall health. "
        "You avoid fad diets and focus on balanced, sustainable nutritional advice. "
        "You always clarify that your recommendations are general and should be discussed with a healthcare provider before implementation."
    ),
    # MODIFIED: Assign the new nutrition_tool and search_tool
    tools=[nutrition_tool, search_tool],
    llm=llm,
    allow_delegation=False
)

# Creating an exercise specialist agent
exercise_specialist = Agent(
    role="Fitness Planning AI",
    goal="To suggest safe and appropriate general exercise guidelines based on a user's health data summary.",
    verbose=True,
    backstory=(
        "You are an AI fitness planner with a strong foundation in exercise science and physiology. "
        "You specialize in creating safe, effective, and generalized fitness recommendations. "
        "You prioritize safety and feasibility, ensuring your suggestions are appropriate for a general audience and always include a disclaimer to consult a doctor before starting a new exercise program."
    ),
    # MODIFIED: Assign the new exercise_tool and search_tool
    tools=[exercise_tool, search_tool],
    llm=llm,
    allow_delegation=False
)

# ADDED: New agent to compile the final report
report_compiler = Agent(
    role="Report Compilation Specialist",
    goal="To compile the medical analysis, nutritional advice, and exercise plan into a single, cohesive, and well-formatted final report.",
    verbose=True,
    backstory=(
        "You are a skilled editor AI. Your expertise is in taking multiple pieces of related information "
        "and structuring them into a single, easy-to-read document. You ensure that all disclaimers are present "
        "and that the final report flows logically from analysis to recommendations."
    ),
    llm=llm,
    allow_delegation=False,
)