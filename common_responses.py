from flask import jsonify, make_response

def invalidJWT():
        response = jsonify({
            "error": "Unauthorized",
            "message": "User not found or JWT is invalid"
        })
        return make_response(response, 401)

def noUser(user_id):
        response = jsonify({
            "error": "User not found",
            "message": f"User with id {user_id} does not exist in the database"
        })
        return make_response(response, 404)

def noNote(note_id):
        response = jsonify({
            "error": "Note not found",
            "message": f"Note with id {note_id} does not exist in the database"
        })
        return make_response(response, 404)

def notAuthorized():
    response = jsonify({
                "error": "Forbidden",
                "message": "Not authorized to access this resource"
            })
    return make_response(response, 403)