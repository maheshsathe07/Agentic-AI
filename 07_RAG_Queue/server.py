from fastapi import FastAPI, Query
from dotenv import load_dotenv

load_dotenv()
from .client.rq_client import queue
from .queues.worker import process_query

app = FastAPI()

@app.get('/')
def root():
    return {"status": "Server is up and running!!"}

@app.post('/chat')
def chat(
        query: str = Query(..., description="The chat query of user")
):
    job = queue.enqueue(process_query, query) # this is the id of the job
    return {"status": "Queued", "job_id": job.id}


@app.get('/job-status')
def get_result(
    job_id: str = Query(..., description="The job id to fetch result back")
):
    job = queue.fetch_job(job_id)
    result = job.return_value()

    return { "result": result }