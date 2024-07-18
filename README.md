# Python REST APIs With Flask

### MariaDB
This project uses MariaDB as the database. You can install MariaDB on your machine by following the instructions on the [official website](https://mariadb.org/).

After installing MariaDB, you can create a database and a user with the following commands:

```console
mariadb -u root -p
CREATE DATABASE users;
CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON users.* TO 'user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

If you would like to use a different database name, user, or password, you can update the `config.toml` file in the `rp_flask_api/` folder.

### Installation & Running
First, navigate to the `rp_flask_api/` folder and create a virtual environment:

```console
cd rp_flask_api
python3 -m venv venv
source venv/bin/activate
```

Install the pinned dependencies from `requirements.txt`:

```console
python -m pip install -r requirements.txt
```

Initialize the database:
```console
python build_database.py
```

Finally, start the development web server:

```console
python run_app.py
```

To see your home page, visit `http://127.0.0.1:8000`. You can find the Swagger UI API documentation on `http://127.0.0.1:8000/api/docs`.


### Testing
To run the tests, you need to set up a test database. You can do this by running the following commands:

```console
myariadb -u root -p
CREATE DATABASE tests;
CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testpassword';
GRANT ALL PRIVILEGES ON tests.* TO 'test'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

If you would like to use a different database name, user, or password, you can update the `config.toml` file in the `rp_flask_api/` folder.

After setting up the test database, you can run the tests with the following command

```console
python run_unit_tests.py
```

If you would like to see unit test coverage, you can run the following command:

```console
python run_coverage.py
```
