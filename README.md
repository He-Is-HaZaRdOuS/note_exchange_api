# NoteExchangeAPI

## Overview

This API, built with Flask, enables user registration, friend management, and note exchange. It features an RBAC (Role-Based Access Control) system for multi-tier administrators with varying privileges. The database setup includes SQLite3 for unit tests and MariaDB for production, environment settings are managed via a config.toml file.

## Features

- **User Registration**: Register new users.
- **Friend Management**: Add and manage friends.
- **Note Exchange**: Exchange notes between users.
- **RBAC System**: Multi-tier admin roles with different access levels.
- **Testing**: Uses SQLite3 in-memory database for unit tests.
- **Database**: Utilizes MariaDB for production environments.
- **Configuration**: Managed via config.toml.
- **Documentation**: OpenAPI docs available courtesy of Swagger and Redoc.

## MariaDB Setup

1. Install MariaDB from the [official website](https://mariadb.org/).
2. Create a database and a user:
    ```bash
    mariadb -u root -p
    CREATE DATABASE users;
    CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON users.* TO 'user'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
    ```
    Update `config.toml` if you use different credentials.

## Installation & Running

1. Navigate to the `note_exchange_api/` folder and create a virtual environment:
    ```bash
    cd note_exchange_api
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Initialize the database:
    ```bash
    python build_database.py
    ```

4. Start the development server:
    ```bash
    python run_app.py
    ```

5. Access the home page at `http://127.0.0.1:8000`. API documentation is available at `http://127.0.0.1:8000/api/docs`.

## Running Tests

1. Run the tests:
    ```bash
    python run_unit_tests.py
    ```

2. To see unit test coverage:
    ```bash
    python run_coverage_tests.py
    ```

## Testing with Postman

1. Download and install Postman from the [official website](https://www.postman.com/downloads/).

2. Create a new request in Postman:
    - Set the method (GET, POST, PUT, DELETE) and URL according to your API endpoints.
    - Add necessary headers (e.g., `Content-Type: application/json`).
    - Include the request body if needed (e.g., JSON data for POST requests).
    - **For protected endpoints**, provide the Bearer token JWT in the `Authorization` header:
      ```
      Authorization: Bearer <your_jwt_token>
      ```

3. Send the request and view the response:
    - Use Postman’s interface to send requests and view server responses, making it easier to test and debug the API.

## License

This project is licensed under the MIT License.
