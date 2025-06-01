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

You can build and run using Docker.

```sh
docker build -t mqtt-latency-test:latest
```

Then, run the container with Docker.

```sh
docker run -d --name mqtt-latency-test -p 8000:8000 mqtt-latency-test:latest
```

## License

This repository is licensed under the MIT License. Contributions are welcome!
