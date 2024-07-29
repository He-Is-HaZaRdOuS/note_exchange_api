# Provide common http responses to rejected requests

from flask import jsonify, make_response

# 400 Bad Request with a specialized message
def badRequest(message):
    response = jsonify({
        "error": "Bad Request",
        "message": message
    })
    return make_response(response, 400)

# 401 Unauthorized
def unauthorized():
    response = jsonify({
        "error": "Unauthorized",
        "message": "User not found or JWT is invalid"
    })
    return make_response(response, 401)

# 403 Forbidden
def forbidden():
    response = jsonify({
        "error": "Forbidden",
        "message": "Not authorized to access this resource"
    })
    return make_response(response, 403)

# 404 Not Found
def notFound():
    response = jsonify({
        "error": "Not Found",
        "message": "Resource not found"
    })
    return make_response(response, 404)
