## Notificator service


- for install dependencies run:
```bash
python3 -m venv env && source env/bin/activate && pip install -r requirements.txt
&& docker compose -f docker-compose.yml build && docker-compose -f docker-compose.yml up -d
```
- for run
```
bash run.sh 
```

### Database Migrations with Alembic

#### Initial Setup
```bash
# Initialize Alembic (if not already initialized)
alembic init migrations
```

#### Working with Migrations

1. Create a new migration:
```bash
# Generate migration automatically based on model changes
alembic revision --autogenerate -m "Description of changes"

# Or create an empty migration
alembic revision -m "Description of changes"
```

2. Apply migrations:
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +1

# Upgrade to a specific revision
alembic upgrade <revision_id>
```

3. Rollback migrations:
```bash
# Rollback last migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Rollback to a specific revision
alembic downgrade <revision_id>
```

4. View migration information:
```bash
# View current revision
alembic current

# View migration history
alembic history

# View pending migrations
alembic history --indicate-current
```

### Common Migration Workflows

1. Making database changes:
```bash
# 1. Make changes to your SQLAlchemy models in lib/models.py
# 2. Generate a new migration
alembic revision --autogenerate -m "Add user table"
# 3. Review the generated migration in migrations/versions/
# 4. Apply the migration
alembic upgrade head
```

2. Fixing a failed migration:
```bash
# 1. Rollback the failed migration
alembic downgrade -1
# 2. Fix the migration file
# 3. Apply the fixed migration
alembic upgrade head
```

fast_video_backend/
├── lib/
│   ├── crud/         # CRUD operations
│   ├── routers/      # API routes
│   ├── db.py         # Database configuration
│   ├── models.py     # SQLAlchemy models
│   └── schemas.py    # Pydantic schemas
├── migrations/       # Alembic migrations
├── alembic.ini      # Alembic configuration
├── main.py          # FastAPI application
└── settings.py      # Application settings

```