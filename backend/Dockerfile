FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --uid 1000 app && chown -R app /app
USER app

ENV PORT=8000
EXPOSE 8000

# Render's free tier has no pre-deploy hook, so migrations run on boot.
# Safe with a single instance; move to a pre-deploy step before scaling out.
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
