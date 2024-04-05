# Use official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update
RUN python3 -m pip install -U yt-dlp
RUN apt-get install ffmpeg -y
RUN pip install ffmpeg-python==0.2.0

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt


# Copy the current directory contents into the container at /app
COPY . .
