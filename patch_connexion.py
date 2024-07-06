PATCH_CODE = """
import json

class FlaskJSONEncoder(json.JSONEncoder):
    pass
"""

def patch_connexion():
    import os
    import connexion
    import re

    # Find the correct path to the flask_app.py file
    conn_file = os.path.join(connexion.__path__[0], 'apps', 'flask_app.py')
    
    with open(conn_file, 'r') as file:
        file_data = file.read()

    new_file_data = re.sub(
        r'class FlaskJSONEncoder\(json\.JSONEncoder\):',
        PATCH_CODE.strip(),
        file_data,
        count=1
    )

    with open(conn_file, 'w') as file:
        file.write(new_file_data)

if __name__ == "__main__":
    patch_connexion()
