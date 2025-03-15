## Notificator service

### Project Status and TODO List

#### Current Status
- [x] Basic project structure
- [x] Database setup with PostgreSQL
- [x] Basic CRUD operations for notifications
- [x] Database migrations with Alembic

#### TODO List

##### Phase 1 - Basic Functionality
- [ ] Email Notifications:
  - [ ] HTML and text format support
  - [ ] File attachments
  - [ ] Different encodings support
  - [ ] Integration with email providers (SendGrid/Amazon SES)

- [ ] Templates System:
  - [ ] Template CRUD operations
  - [ ] Template versioning
  - [ ] Variable substitution
  - [ ] Template preview functionality

- [ ] API Development:
  - [ ] Complete notification endpoints
  - [ ] Template management endpoints
  - [ ] API documentation (Swagger/OpenAPI)

##### Phase 2 - Extended Features
- [ ] SMS Notifications:
  - [ ] Unicode support
  - [ ] Automatic message splitting
  - [ ] Delivery status tracking
  - [ ] SMS provider integration (Twilio/Nexmo)

- [ ] Message Queue Integration:
  - [ ] RabbitMQ/Kafka setup
  - [ ] Separate queues for different notification types
  - [ ] Dead Letter Queue for error handling

- [ ] Caching:
  - [ ] Redis integration
  - [ ] Template caching
  - [ ] Rate limiting implementation

##### Phase 3 - Security & Reliability
- [ ] Security Features:
  - [ ] JWT authentication
  - [ ] API key management
  - [ ] RBAC implementation
  - [ ] Data encryption (AES-256)
  - [ ] TLS 1.3 support

- [ ] Monitoring & Logging:
  - [ ] Prometheus metrics
  - [ ] Grafana dashboards
  - [ ] ELK Stack integration
  - [ ] Sensitive data masking in logs

- [ ] Performance & Testing:
  - [ ] Load testing (1000+ notifications/minute)
  - [ ] API response time optimization (<200ms)
  - [ ] Test coverage >80%
  - [ ] Failover mechanisms

### Installation and Setup

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
```
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
 ### issues:
 - [x] fix notification endpoint, for send
 - [x] up worker for handle producer notifications
 - [ ] correct handle with consumer need to fix update_notification function
 - [ ] implement full logic send\handle\result