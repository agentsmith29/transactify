# Transactify Terminal

## Usage
All settings are store in the [`.env`-File](./.env) and in the [`docker-compose.yaml`](./docker-compose.yaml) File. In the `.env`-File, change
the port and the host.
```
.env
PROJECT_HOST=192.168.1.190
PROJECT_PORT=8000

```
## First time running the project
In each django application [`transactify_service`](./transactify_service/) and  [`transactify_terminal`](./transactify_terminal/) a entrypoint file is placed. Uncomment the following lines
```bash
#chmod +x make_migrations.sh
chmod +x make_store_db_migration.sh
# run make migrations
./make_store_db_migration.sh
```
which triggers the migration of the PostgreSQL Database. Please note, that a run of this script, also removes the whole database, thus make sure it is only run when using a fresh installation.

## Running the project
To run this project, use the docker-compose file. All other things are setup automatically.
```bash
docker-compose up --build
```

## Running the tests
```bash
docker-compose -f docker-compose.tests.yaml up --build
```
