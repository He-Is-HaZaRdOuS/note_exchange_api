import os

# Set the environment variable to determine the app configuration
os.environ['CONFIG'] = 'DEVELOPMENT'

from application import app


# Run the Flask app
if __name__ == "__main__":
    app.run()
