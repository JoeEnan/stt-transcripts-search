# How to Run the Project with Docker Compose

## Prerequisites

1. **Install Docker**
   - For **Windows**, install [Docker Desktop](https://www.docker.com/products/docker-desktop).
   - For **Linux**, install [Docker based on your distribution](https://docs.docker.com/engine/install/).

2. **Verify Installation**
   - Check that Docker is running:
     ```bash
     docker --version
     ```
   - Check that Docker Compose is installed:
     ```bash
     docker-compose --version
     ```

## Running the Project

1. **Clone the Repository**
   - Clone the project repository to your local machine:
     ```bash
     git clone https://github.com/JoeEnan/stt-transcripts-search.git
     cd stt-transcripts-search
     ```

2. **Build and Run Docker Containers**
   - Use the following command to build the Docker images and start the containers:
     ```bash
     docker compose up --build
     ```

3. **Follow Logs**
   - To follow the logs of the backend or frontend services during testing, use the following commands in separate terminals:
   - For backend logs:
     ```bash
     docker compose -f docker-compose.yml logs -f backend_test
     ```
   - For frontend logs:
     ```bash
     docker compose -f docker-compose.yml logs -f frontend_test
     ```


# How to Run Frontend and Backend Unit Tests with Docker Compose
To run the unit tests for both backend and frontend, use the following command:
```shell
docker compose -f docker-compose.test.yml up --build --remove-orphans --force-recreate
```

To follow the logs of the backend or frontend services during testing, use the following commands:
- `docker compose -f docker-compose.test.yml logs -f backend_test`
- `docker compose -f docker-compose.test.yml logs -f frontend_test`


## Note: Verbosity on Frontend Tests
In the `docker-compose.test.yml` file, there is an environment variable `JEST_SILENT`. This variable controls whether Jest output should be silenced during tests. If you want to see the Jest output, set this variable to `false`.

# How to Run the Project Locally

## Prerequisites
Ensure you have the following software installed on your machine:

- **Python** (3.12 or above)
- **Node.js** (version 18.x or above)
- **uv** (a fast Python package manager and project manager written in Rust)

## Installing UV
You can install `uv` using the following command:

```shell
pip install uv
```

After installing `uv`, sync all dependencies with:

```shell
cd backend
uv sync --all-extras
```

## Installing Frontend Dependencies
For the frontend, ensure you have `npm` installed and run the following command:

```shell
cd frontend
npm install
```

## Running the Project Locally
To run the project locally, follow these steps:

1. **Backend**:
- Navigate to the backend directory.
- Run the following command to start the backend server:

```shell
uv run main.py
```

2. **Frontend**:
- Navigate to the frontend directory.
- Run the following command to start the frontend development server:

```shell
npm run dev
```