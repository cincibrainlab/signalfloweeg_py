brew install postgresql@14

# Start postgresql
/opt/homebrew/opt/postgresql@14/bin/postgres -D /opt/homebrew/var/postgresql@14

# Option 2 for startup: 
brew services start postgresql@14

# Create a new database
createdb -h 127.0.0.1 -p 5432 airflow_db

dropdb -h 127.0.0.1 -p 5432 airflow_db
createdb -h 127.0.0.1 -p 5432 airflow_db


psql -h 127.0.0.1 -p 5432 -c "CREATE USER airflow_user WITH PASSWORD 'airflow_pass';"
psql -h 127.0.0.1 -p 5432 -c "GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;"
psql -h 127.0.0.1 -p 5432 -c "GRANT ALL ON SCHEMA public TO airflow_user;"


