import uvicorn
from fastapi import FastAPI, status
import time
from celery import Celery
from celery.result import AsyncResult
from media.client.factory import create_media_client
from media.config import CeleryConfiguration
from pydantic import BaseModel

app = FastAPI()
VERSION = "/v1"

# Configure Celery
celery = Celery('app', broker=CeleryConfiguration.BROKER, backend=CeleryConfiguration.BACKEND)


class InputMediaUrlBody(BaseModel):
    url: str


# Define Celery task
@celery.task(bind=True, time_limit=300)  # Set a task timeout of 30 seconds
def get_transcript(self, url):
    start_time = time.time()
    try:
        media_client = create_media_client(url)
        transcript = media_client.get_transcript(url)
        elapsed_time_seconds = time.time() - start_time
        return {"url": url, "transcript": transcript, "elapsed_seconds": elapsed_time_seconds}
    except Exception as e:
        # Handle exceptions gracefully and log errors
        print(f"Error processing transcript for {url}: {e}")
        raise


# Endpoint to start the task
@app.post(VERSION + '/media', status_code=status.HTTP_200_OK)
async def start_task(body: InputMediaUrlBody):
    task = get_transcript.delay(body.url)
    return {'task_id': task.id}


# Endpoint to get task status and result
@app.get(VERSION + '/media/{task_id}', status_code=status.HTTP_200_OK)
async def get_info(task_id: str):
    task = AsyncResult(task_id, app=celery)
    if task.state == 'SUCCESS':
        result = task.result
        response = {
            'task_id': task_id,
            'status': task.state,
            'transcript': result['transcript'],
            'url': result['url'],
            'elapsed_seconds': result['elapsed_seconds']
        }
    else:
        response = {'task_id': task_id, 'status': task.state}
    return response


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
