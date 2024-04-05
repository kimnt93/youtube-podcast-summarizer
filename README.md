## Media Transcription Service

This service simplifies media file transcription (YouTube, Spotify) using Celery and FastAPI. Its API enables asynchronous transcription via the [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text) to deliver accurate and efficient transcriptions.



### Environment Variables

Before running the service, ensure you have the following environment variables configured:

- **CELERY_BROKER**: URL for the Celery broker.
- **CELERY_BACKEND**: URL for the Celery backend.
- **OPENAI_API_KEY**: API key for accessing OpenAI services.
- **API_VERSION**: Version of the OpenAI API to use.
- **SPOTIFY_CLIENT_ID**: Client ID for accessing Spotify services.
- **SPOTIFY_CLIENT_SECRET**: Client secret for accessing Spotify services.

### Usage

1. Set up the required environment variables:

```bash
export CELERY_BROKER=<broker_url>
export CELERY_BACKEND=<backend_url>
export OPENAI_API_KEY=<openai_api_key>
export API_VERSION=<api_version>
export SPOTIFY_CLIENT_ID=<spotify_client_id>
export SPOTIFY_CLIENT_SECRET=<spotify_client_secret>
```

2. Run the server:
```
docker-compose up -d
```

3. Access the API at `http://127.0.0.1:8000`.

### API Endpoints

#### Start Task

- **URL:** `/v1/media`
- **Method:** `POST`
- **Description:** Initiates a task to transcribe a media file.
- **Request Body:**
  ```json
  {
    "url": "string"
  }
  ```
  - `url`: URL of the media file to transcribe.
- **Response:**
  ```json
  {
    "task_id": "string"
  }
  ```
  - `task_id`: Unique identifier for the initiated task.

#### Get Task Information

- **URL:** `/v1/media/{task_id}`
- **Method:** `GET`
- **Description:** Retrieves the status and result of a previously initiated task.
- **Path Parameters:**
  - `task_id`: ID of the task to retrieve information for.
- **Response:**
  - If the task is completed successfully:
    ```json
    {
      "task_id": "string",
      "status": "SUCCESS",
      "transcript": "string",
      "url": "string",
      "elapsed_seconds": float
    }
    ```
  - If the task is still pending or failed:
    ```json
    {
      "task_id": "string",
      "status": "PENDING" | "FAILURE"
    }
    ```

### Dependencies

- [FastAPI](https://fastapi.tiangolo.com/): Web framework for building APIs with Python 3.7+.
- [Celery](https://docs.celeryproject.org/en/stable/): Distributed task queue for executing tasks asynchronously.
- [uvicorn](https://www.uvicorn.org/): ASGI server for running FastAPI applications.

## API Documentation

### Media Transcription Service API

#### Start Task

- **URL:** `/v1/media`
- **Method:** `POST`
- **Request Body:**
  - `url` (string): URL of the media file to transcribe.

#### Get Task Information

- **URL:** `/v1/media/{task_id}`
- **Method:** `GET`
- **Path Parameters:**
  - `task_id` (string): ID of the task to retrieve information for.

For more details on each endpoint, please refer to the provided README or inspect the API directly.