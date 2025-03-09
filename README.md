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
     docker compose version
     ```
     - Ensure that docker compose is at least v2

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
     docker compose logs -f backend_test
     ```
   - For frontend logs:
     ```bash
     docker compose logs -f frontend_test
     ```

4. **Access the webpage**
   - To access the webpage, go to http://localhost:3000 after the build completes.

# How to Run Frontend and Backend Unit Tests with Docker Compose
To run the unit tests for both backend and frontend, use the following command:
```shell
docker compose -f docker-compose.test.yml up --build --remove-orphans --force-recreate
```

To follow the logs of the backend or frontend services during testing, use the following commands:
- `docker compose -f docker-compose.test.yml logs -f backend_test`
- `docker compose -f docker-compose.test.yml logs -f frontend_test`


All tests from should pass. Current build output shows:
```shell
backend_test-1   | ============================= test session starts ==============================
backend_test-1   | platform linux -- Python 3.12.9, pytest-8.3.5, pluggy-1.5.0
backend_test-1   | rootdir: /app
backend_test-1   | configfile: pyproject.toml
backend_test-1   | plugins: anyio-4.8.0, asyncio-0.25.3
backend_test-1   | asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function
backend_test-1   | collected 4 items
backend_test-1   | 
backend_test-1   | tests/test_unit.py ....                                                  [100%]
backend_test-1   | 
backend_test-1   | ============================== 4 passed in 0.67s ===============================
backend_test-1 exited with code 0
frontend_test-1  | PASS src/components/Notification.test.jsx
frontend_test-1  | PASS src/components/HealthStatus.test.jsx
frontend_test-1  | PASS src/components/TranscriptionList.test.jsx
frontend_test-1  | PASS src/components/FileUpload.test.jsx
frontend_test-1  | 
frontend_test-1  | Test Suites: 4 passed, 4 total
frontend_test-1  | Tests:       21 passed, 21 total
frontend_test-1  | Snapshots:   0 total
frontend_test-1  | Time:        1.862 s
frontend_test-1 exited with code 0

```

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