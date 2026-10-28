#!/bin/sh
# TASK-003: create the restricted application role (ADR-004 section 5).
#
# Runs once, as the bootstrap role POSTGRES_USER, from the official image's
# /docker-entrypoint-initdb.d mechanism. IMPORTANT: initdb scripts run ONLY when
# the data directory is empty (a fresh volume). Changing this file or the
# password variables later has no effect on an existing volume; to re-run it:
#   docker compose down -v && docker compose up -d db      (this deletes all data)
#
# Roles after this script:
#   owner  = POSTGRES_USER (created by the image, owns database POSTGRES_DB);
#            used by Alembic through DATABASE_MIGRATION_URL.
#   app    = APP_DB_USER (created here); used by the backend through DATABASE_URL.
#            Non-owner, non-superuser, no DDL, no BYPASSRLS; SELECT, INSERT,
#            UPDATE, DELETE on the owner's tables and USAGE on its sequences.
#
# Passwords come from the environment and are passed to psql as variables
# (quoted by psql with :'name' / :"name"); no password is written in this file.
set -eu

: "${POSTGRES_USER:?POSTGRES_USER is not set}"
: "${POSTGRES_DB:?POSTGRES_DB is not set}"
: "${APP_DB_USER:?APP_DB_USER is not set}"
: "${APP_DB_PASSWORD:?APP_DB_PASSWORD is not set}"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v owner="$POSTGRES_USER" \
  -v dbname="$POSTGRES_DB" \
  -v app_user="$APP_DB_USER" \
  -v app_password="$APP_DB_PASSWORD" <<'SQL'
-- Restricted runtime role: no superuser, no DDL rights, no BYPASSRLS.
CREATE ROLE :"app_user" WITH LOGIN PASSWORD :'app_password'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

-- Connect and use the schema, but never create objects in it.
GRANT CONNECT ON DATABASE :"dbname" TO :"app_user";
GRANT USAGE ON SCHEMA public TO :"app_user";
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM :"app_user";

-- Tables and sequences do not exist yet (Alembic creates them as the owner), so
-- grant on whatever the owner creates later in schema public.
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :"app_user";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
  GRANT USAGE ON SEQUENCES TO :"app_user";
SQL
