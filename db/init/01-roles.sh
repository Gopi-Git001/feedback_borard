#!/bin/sh
# TASK-003: create the restricted application role (ADR-004 section 5).
#
# Runs once, as the bootstrap role POSTGRES_USER, from the official image's
# /docker-entrypoint-initdb.d mechanism. IMPORTANT: PostgreSQL's image runs initdb
# scripts ONLY when the data directory is empty (a fresh volume). Changing this
# file or the password variables later has no effect on an existing volume by
# itself. Two ways to apply a change:
#   - start fresh (deletes all data):  docker compose down -v && docker compose up -d db
#   - re-run by hand on the live db (the script is idempotent, so this is safe;
#     it also re-syncs the app role password from APP_DB_PASSWORD):
#       docker compose exec db sh /docker-entrypoint-initdb.d/01-roles.sh
#
# Roles after this script:
#   owner  = POSTGRES_USER (created by the image, owns database POSTGRES_DB);
#            used by Alembic through DATABASE_MIGRATION_URL. Alembic runs ONLY as
#            the owner. (In the official image this role is a superuser.)
#   app    = APP_DB_USER (created here); used by the backend through DATABASE_URL.
#            Non-owner, non-superuser, no DDL, no BYPASSRLS; SELECT, INSERT,
#            UPDATE, DELETE on the owner's tables and USAGE on its sequences.
#            It is the only role other than the owner that may connect to the
#            database (all PUBLIC privileges on it are revoked).
#
# After the FIRST Alembic migration, run db/ops/revoke-app-on-alembic-version.sh:
# the default privileges below would otherwise let the app role read and write
# the alembic_version table.
#
# No password is ever in this file or on a command line: the values are read by
# psql from the environment (\getenv, psql 15+) and quoted by psql (:'name', :"name").
# psql still sends the password inside one statement (ALTER ROLE ... PASSWORD), so
# the session also tells the server not to echo failing statements into its log
# (SET log_min_error_statement = panic) and psql not to print error context.
set -eu

: "${POSTGRES_USER:?POSTGRES_USER is not set}"
: "${POSTGRES_DB:?POSTGRES_DB is not set}"
: "${APP_DB_USER:?APP_DB_USER is not set}"
: "${APP_DB_PASSWORD:?APP_DB_PASSWORD is not set}"

if [ "$APP_DB_USER" = "$POSTGRES_USER" ]; then
  echo "01-roles.sh: APP_DB_USER must differ from POSTGRES_USER (the owner role)" >&2
  exit 2
fi

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv owner POSTGRES_USER
\getenv dbname POSTGRES_DB
\getenv app_user APP_DB_USER
\getenv app_password APP_DB_PASSWORD

-- Keep the password out of the server log even when a statement fails: a failing
-- statement is otherwise logged with its text, which contains the password.
-- Session-level settings (superuser); they end with this psql session.
SET log_min_error_statement = panic;
SET log_statement = 'none';
SET log_min_duration_statement = -1;
-- Terse errors: psql prints no "LINE n:" query excerpt.
\set VERBOSITY terse

-- Create the restricted runtime role only if it does not exist yet.
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_user') AS create_app_role \gset
\if :create_app_role
  CREATE ROLE :"app_user" WITH LOGIN;
\endif

-- Always (re)apply the attributes and the password: no superuser, no DDL rights,
-- no BYPASSRLS; the password follows APP_DB_PASSWORD.
ALTER ROLE :"app_user" WITH LOGIN PASSWORD :'app_password'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

-- Only the owner (owner of the database; a superuser in the official image) and
-- the app role may connect. No PUBLIC privilege (CONNECT, TEMPORARY, CREATE) is left.
REVOKE ALL ON DATABASE :"dbname" FROM PUBLIC;
REVOKE ALL ON DATABASE :"dbname" FROM :"app_user";
GRANT CONNECT ON DATABASE :"dbname" TO :"app_user";

-- Use the schema, but never create objects in it.
GRANT USAGE ON SCHEMA public TO :"app_user";
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM :"app_user";

-- Tables and sequences do not exist yet (Alembic creates them as the owner), so
-- grant on whatever the owner creates later in schema public. Repeating these
-- statements does not change anything.
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :"app_user";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
  GRANT USAGE ON SEQUENCES TO :"app_user";
SQL
