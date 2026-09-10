# Concepts - Phase 01

## FastAPI

## Definition

FastAPI is a Python web framework for building HTTP APIs.

## Why it exists

It makes API development fast while providing request validation, automatic documentation, and strong typing support.

## How it works

FastAPI maps Python functions to HTTP routes. It uses type hints and Pydantic models to validate data and generate OpenAPI documentation.

## Architecture position

FastAPI is the service layer of this project.

```text
Client -> FastAPI -> future video processing / model inference
```

## Example in our project

`GET /health` confirms the process is alive.

`GET /ready` confirms the service is ready to receive traffic.

## Alternatives

- Flask: simpler, less built-in validation
- Django: larger full-stack framework
- Litestar: modern alternative with similar goals

## Advantages

- Type-friendly
- Good documentation support
- Common in Python ML serving
- Works well with Docker and Kubernetes

## Limitations

- It does not solve background jobs by itself.
- It does not make slow model inference magically fast.

## Production considerations

Production deployments usually run FastAPI behind an ASGI server such as Uvicorn or Gunicorn with Uvicorn workers.

## Security considerations

APIs should validate input, avoid exposing internal errors, and avoid binding public interfaces unnecessarily during local development.

## Common mistakes

- Putting heavy model loading inside every request
- Returning stack traces to users
- Treating `/health` and `/ready` as the same thing

## Interview questions

- Why use FastAPI for ML serving?
- What is ASGI?
- What is the difference between health and readiness?

## Interview answers

FastAPI is useful for ML serving because it provides a clean HTTP interface, validation, generated API docs, and async support. Health means the process is alive. Readiness means the app is prepared to serve traffic.

## Commands to remember

```powershell
.venv\Scripts\python -m uvicorn footballmatch_api.main:app --host 127.0.0.1 --port 8000
```

## Mental model / workflow

Write endpoint -> validate with test -> run app locally -> later package in Docker.

## Virtual Environment

## Definition

A virtual environment is an isolated Python environment for one project.

## Why it exists

It prevents dependencies from different projects from conflicting with each other.

## How it works

Python creates a local folder containing its own interpreter entry points and package directory. `pip` installs packages there.

## Architecture position

It belongs to local development, not production runtime.

## Example in our project

`.venv` contains FastAPI, pytest, Ruff, and related dependencies.

## Alternatives

- Conda
- Poetry environments
- uv-managed environments
- system Python

## Advantages

- Simple
- Built into Python
- Easy to ignore in Git

## Limitations

- Not identical to Docker or production
- Can drift if dependencies are not pinned

## Production considerations

Production commonly uses container images instead of manually managed virtual environments.

## Security considerations

Do not commit `.venv`. Rebuild it from dependency files.

## Common mistakes

- Installing project dependencies globally
- Forgetting to activate or use the venv Python
- Committing `.venv`

## Interview questions

- Why use a virtual environment?
- Why should `.venv` be ignored by Git?

## Interview answers

A virtual environment isolates dependencies for one project. `.venv` should not be committed because it is machine-specific and can be recreated from dependency files.

## Commands to remember

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Mental model / workflow

Project dependency file -> virtual environment -> install -> test.

## Docker

## Definition

Docker packages an application and its runtime dependencies into an image that can run as a container.

## Why it exists

It reduces environment differences between developer machines, CI, and servers.

## How it works

A Dockerfile defines filesystem layers. Docker builds those layers into an image. Running the image creates a container, which is an isolated process with its own filesystem and network namespace.

## Architecture position

Docker packages the FastAPI service before Compose, CI, and Kubernetes.

## Example in our project

The Dockerfile installs the Python package and starts Uvicorn on port 8000.

## Alternatives

- Native virtual environments
- Podman
- systemd services
- virtual machines

## Advantages

- Portable runtime
- Good CI/CD integration
- Natural path to Kubernetes

## Limitations

- Images must be rebuilt after dependency changes
- Poor Dockerfiles can create large or insecure images

## Production considerations

Images should use small bases, avoid secrets, and run as non-root where feasible.

## Security considerations

The current Dockerfile creates a non-root `app` user.

## Common mistakes

- Copying `.venv` into images
- Running containers as root unnecessarily
- Baking secrets into images

## Interview questions

- What is the difference between an image and a container?
- Why run containers as non-root?

## Interview answers

An image is the packaged template. A container is a running instance of that image. Running as non-root reduces the impact if the application is compromised.

## Commands to remember

```powershell
docker build -t footballmatch-api:dev .
docker run --rm -p 8000:8000 footballmatch-api:dev
```

## Mental model / workflow

Code -> Dockerfile -> image -> container -> later Kubernetes pod.
