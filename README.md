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
     - **IMPORTANT**: Ensure that Docker Compose is version 2 or higher.
  - **For Docker Desktop Users**: Please ensure that Docker Engine is running before proceeding

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
     docker compose logs -f backend
     ```
   - For frontend logs:
     ```bash
     docker compose logs -f frontend
     ```

4. **Access the Webpage**
   - Once Docker Compose has finished building both containers, go to [http://localhost:3000](http://localhost:3000) to access the webpage.
   - Once audio file upload request has been sent, allow the application some time to download the model.
      - The notification that the audio file is processed will come shortly

# Running Frontend and Backend Unit Tests with Docker Compose

To run the unit tests for both the backend and frontend, use the following command:
```bash
docker compose -f docker-compose.test.yml up --build --remove-orphans --force-recreate
```

Based on the information from the `README.md` and other provided files, here’s how you can answer a question about where readers can find the test files:

---

## Where to Find Test Files

In the project, you can find the test files located in the `backend/tests` and `frontend/src/components` directories. 

### Backend Tests
- **Test files for backend functionalities are located in:**
  - `backend/tests/test_unit.py`
  - This file contains unit tests for database operations, transcription functionalities, and other backend-related tests.

### Frontend Tests
- **Test files for frontend components are found in:**
  - `frontend/src/components/FileUpload.test.jsx` - Unit Tests for the FileUpload component.
  - `frontend/src/components/HealthStatus.test.jsx` - Unit Tests for the HealthStatus component.
  - `frontend/src/components/Notification.test.jsx` - Unit Tests for the Notification component.
  - `frontend/src/components/TranscriptionList.test.jsx` - Unit Tests for the TranscriptionList component.

To follow the logs of the backend or frontend services during testing, use the following commands:
- For backend logs:
  ```bash
  docker compose -f docker-compose.test.yml logs -f backend_test
  ```
- For frontend logs:
  ```bash
  docker compose -f docker-compose.test.yml logs -f frontend_test
  ```

All tests should pass. The current build output shows:
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

## Note on Verbosity for Frontend Tests
In the `docker-compose.test.yml` file, there is an environment variable named `JEST_SILENT`. This variable controls whether Jest output is silenced during tests. If you want to see the Jest output, set this variable to `false`.

# Running the Project Locally

## Prerequisites
Ensure you have the following software installed on your machine:

- **Python** (3.12 or above)
- **Node.js** (version 18.x or above)
- **uv** (a fast Python package and project manager written in Rust)

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
