# Changelog

## Unreleased

- Moved persistent application storage from MongoDB to PostgreSQL with an
  append-only Alembic initial schema.
- Added one-container deployment support: FastAPI serves the production React
  build from the root Docker image.
- Removed automatic demo-account seeding from runtime startup.
