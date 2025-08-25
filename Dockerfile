FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p eng_audio_files_mp3 && chmod 755 eng_audio_files_mp3

ENV HOST=db
ENV PORT=5432
ENV DB_NAME=EngStudyBot
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres

CMD ["python", "main.py"]
