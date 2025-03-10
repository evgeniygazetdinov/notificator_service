source env/bin/activate
docker compose -f docker-compose.yml up -d db 
uvicorn main:app --port 8087  --reload
