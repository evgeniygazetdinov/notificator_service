source env/bin/activate
docker compose -f docker-compose.yml up -d
uvicorn main:app --port 8087  --reload
