# Python REST APIs With Flask, Marshmallow, SQLAlchemy, JWT, Redoc and Swagger

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

Then initialize the database:
```console
(venv) $ cd rp_flask_api
(venv) $ python build_database.py
```

Finally, start the development web server:

```console
(venv) $ python run.py
```

To run the tests, use the following command
```console
(venv) $ python run_tests.py
```

To see your home page, visit `http://127.0.0.1:8000`. You can find the Swagger UI API documentation on `http://127.0.0.1:8000/api/docs`.
