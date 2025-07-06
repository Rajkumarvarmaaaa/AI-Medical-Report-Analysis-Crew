import os
from crewai import Crew, Process

# Import all agents and tasks
from agents import doctor, verifier, nutritionist, exercise_specialist, report_compiler
from task import verification, help_patients, nutrition_analysis, exercise_planning, compile_report_task

# Import Celery app and DB components
from celery_app import celery_app
from database import SessionLocal, AnalysisResult, JobStatus

@celery_app.task(bind=True)
def run_crew_analysis(self, query: str, file_path: str, result_id: int):
    """
    Celery task to run the full medical analysis crew and save the result to the database.
    """
    db = SessionLocal()
    try:
        # Update status to RUNNING in the database
        db.query(AnalysisResult).filter(AnalysisResult.id == result_id).update({"status": JobStatus.RUNNING})
        db.commit()

        # Assemble the full crew with all agents and tasks
        medical_crew = Crew(
            agents=[verifier, doctor, nutritionist, exercise_specialist, report_compiler],
            # IMPORTANT: The final task must be the compile_report_task
            tasks=[verification, help_patients, nutrition_analysis, exercise_planning, compile_report_task],
            process=Process.sequential,
            verbose=True # Use verbose=2 for detailed logs in the worker
        )

        # Kick off the crew with the provided inputs
        result = medical_crew.kickoff({'query': query, 'file_path': file_path})
        
        # Update the database with the final report and SUCCESS status
        db.query(AnalysisResult).filter(AnalysisResult.id == result_id).update({
            "final_report": str(result),
            "status": JobStatus.SUCCESS
        })
        db.commit()
        
        return {"status": "Complete", "result_id": result_id, "final_report": str(result)}

    except Exception as e:
        # If an error occurs, update the status to FAILURE and store the error message
        error_message = f"An error occurred: {str(e)}"
        db.query(AnalysisResult).filter(AnalysisResult.id == result_id).update({
            "final_report": error_message,
            "status": JobStatus.FAILURE
        })
        db.commit()
        # You might want to re-raise the exception for Celery to mark it as a failure
        raise e
    finally:
        db.close()