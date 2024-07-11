# Python REST APIs With Flask, Marshmallow, SQLAlchemy, JWT, Redoc and Swagger

You should first create a virtual environment:

```console
$ python -m venv venv
$ source venv/bin/activate
```

Install the pinned dependencies from `requirements.txt`:

```console
(venv) $ python -m pip install -r requirements.txt
```

Then, navigate into the `rp_flask_api/` folder and initialize the database:
```console
(venv) $ cd rp_flask_api
(venv) $ python build_database.py
```

Finally, start the development web server:

```console
(venv) $ python app.py
```

To see your home page, visit `http://127.0.0.1:8000`. You can find the Swagger UI API documentation on `http://127.0.0.1:8000/api/docs`.
