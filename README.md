# Python REST APIs With Flask

### MariaDB
This project uses MariaDB as the database. You can install MariaDB on your machine by following the instructions on the [official website](https://mariadb.org/).

After installing MariaDB, you can create a database and a user with the following commands:

```console
$ mariadb -u root -p
MariaDB [(none)]> CREATE DATABASE users;
MariaDB [(none)]> CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
MariaDB [(none)]> GRANT ALL PRIVILEGES ON users.* TO 'user'@'localhost';
MariaDB [(none)]> FLUSH PRIVILEGES;
MariaDB [(none)]> EXIT;
```

If you would like to use a different database name, user, or password, you can update the `config.toml` file in the `rp_flask_api/` folder.

### Installation & Running
First, navigate to the `rp_flask_api/` folder and create a virtual environment:

```console
$ cd rp_flask_api
$ python -m venv venv
$ source venv/bin/activate
```

Install the pinned dependencies from `requirements.txt`:

```console
(venv) $ python -m pip install -r requirements.txt
```

Initialize the database:
```console
(venv) $ python build_database.py
```

Finally, start the development web server:

```console
(venv) $ python run_app.py
```

To see your home page, visit `http://127.0.0.1:8000`. You can find the Swagger UI API documentation on `http://127.0.0.1:8000/api/docs`.


### Testing
To run the tests, you need to set up a test database. You can do this by running the following commands:

```console
$ myariadb -u root -p
MariaDB [(none)]> CREATE DATABASE tests;
MariaDB [(none)]> CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testpassword';
MariaDB [(none)]> GRANT ALL PRIVILEGES ON tests.* TO 'test'@'localhost';
MariaDB [(none)]> FLUSH PRIVILEGES;
MariaDB [(none)]> EXIT;
```

If you would like to use a different database name, user, or password, you can update the `config.toml` file in the `rp_flask_api/` folder.

After setting up the test database, you can run the tests with the following command

```console
(venv) $ python run_unit_tests.py
```

If you would like to see unit test coverage, you can run the following command:

```console
(venv) $ python run_coverage.py
```
