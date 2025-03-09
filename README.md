# How to Run Unit Tests
To run the unit tests for both backend and frontend, use the following command:
```shell
docker compose -f docker-compose.test.yml up --build --remove-orphans --force-recreate
```

To follow the logs of the backend or frontend services during testing, use the following commands:
- `docker compose -f docker-compose.test.yml logs -f backend_test`
- `docker compose -f docker-compose.test.yml logs -f frontend_test`


## Note: Verbosity on Frontend Tests
In the `docker-compose.test.yml` file, there is an environment variable `JEST_SILENT`. This variable controls whether Jest output should be silenced during tests. If you want to see the Jest output, set this variable to `false`.