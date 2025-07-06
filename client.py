import os
from worker import run_crew_analysis
from database import SessionLocal, AnalysisResult, JobStatus

def submit_analysis_job(query: str, file_path: str = "data/sample.pdf"):
    """
    Submits an analysis job to the Celery queue and creates a corresponding DB record.
    """
    # Ensure the file exists before submitting
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    db = SessionLocal()
    try:
        # 1. Create a record in the database to track the job
        new_analysis = AnalysisResult(
            file_path=file_path,
            query=query,
            status=JobStatus.PENDING,
            task_id="temp" # Temporary task_id
        )
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        
        # 2. Submit the job to the Celery queue
        # Pass the database record ID to the worker
        task = run_crew_analysis.delay(query=query, file_path=file_path, result_id=new_analysis.id)

        # 3. Update the database record with the actual Celery task ID
        new_analysis.task_id = task.id
        db.commit()
        
        print(f"✅ Job submitted successfully!")
        print(f"   - Database Record ID: {new_analysis.id}")
        print(f"   - Celery Task ID: {task.id}")
        
        return task.id

    except Exception as e:
        print(f"❌ Error submitting job: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    # Set up your test PDF path
    test_pdf = "data/sample.pdf"  # Make sure this file exists
    # Set your test query
    query = "Summarise my Blood Test Report and give me some health recommendations"

    print("--- Submitting Medical Report Analysis Job ---")
    print(f"File: {test_pdf}")
    print(f"Query: '{query}'")
    
    task_id = submit_analysis_job(query=query, file_path=test_pdf)

    if task_id:
        print("\nYour request is being processed in the background.")
        print("You can monitor the status by checking the 'analysis_results' table in your database.")