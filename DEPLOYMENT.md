# Deployment

The application uses PostgreSQL. The database URL must be supplied only through
the `DATABASE_URL` environment variable, in SQLAlchemy async form:

`postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE`

## Local development

Start PostgreSQL and apply the schema with:

```bash
docker compose up --build
```

The `migrate` service runs `alembic upgrade head` once before the backend
starts. Do not run schema migrations automatically in the managed application
container; apply `backend/alembic` revisions as a separate release operation.

## aidrop.it runtime

The root `Dockerfile` is the managed runtime entry point. It builds the React
client and serves it from the FastAPI process on port `8000`.

Required runtime values are `DATABASE_URL` and `SECRET_KEY`. Add Sentry or
OpenAI values only when that integration is configured: `OPENAI_API_KEY`,
`APP_SENTRY_DSN`, `SENTRY_API_TOKEN`, and `SENTRY_ORG_SLUG`.

The old MongoDB data is not copied by this repository change. Export it from
the source environment and import it through a separately reviewed migration
job after the PostgreSQL schema is provisioned.
