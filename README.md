# MQTT Latency Test

This repository host webhooks from EMQX MQTT broker as a latency testing.

## Installation

Install Poetry as a Python package manager.

```sh
sudo apt install pipx
pipx install poetry
```

Then, install the dependencies using `poetry`.

```sh
poetry install
```

## Running

You can run the package using `poetry`.

```sh
poetry run fastapi run src/mqtt_latency_test/main.py
```

## Docker

You can build and run using Docker with persistent database storage.

### Option 1: Using Docker Compose (Recommended)

```sh
docker-compose up -d
```

This will:

- Build the image
- Create a named volume for persistent database storage
- Start the container with proper port mapping
- Include health checks and restart policies

### Option 2: Using Docker directly

Build the image:

```sh
docker build -t mqtt-latency-test:latest .
```

Run with a named volume for persistent storage:

```sh
docker run -d \
  --name mqtt-latency-test \
  -p 8000:8000 \
  -v mqtt_data:/app/data \
  -e DATABASE_PATH=/app/data/database.db \
  mqtt-latency-test:latest
```

### Option 3: Using bind mount to local directory

Create a data directory and run with bind mount:

```sh
mkdir -p ./data
docker run -d \
  --name mqtt-latency-test \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_PATH=/app/data/database.db \
  mqtt-latency-test:latest
```

### Database Persistence

The SQLite database is stored in `/app/data/database.db` inside the container. This directory is mounted as a volume to ensure data persistence across container restarts.

- **Named volume**: Data persists in Docker's volume storage
- **Bind mount**: Data is stored in your local `./data` directory

## License

This repository is licensed under the MIT License. Contributions are welcome!
