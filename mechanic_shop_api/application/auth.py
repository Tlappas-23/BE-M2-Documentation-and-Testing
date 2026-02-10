from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import current_app, jsonify, request
from jose import JWTError, ExpiredSignatureError, jwt


def encode_token(customer_id):
    now = datetime.now(timezone.utc)
    expires_in = current_app.config["JWT_EXPIRES_IN"]
    payload = {
        "sub": str(customer_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
    }
    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def token_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header."}), 401

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return jsonify({"error": "Missing token."}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=[current_app.config["JWT_ALGORITHM"]],
            )
        except ExpiredSignatureError:
            return jsonify({"error": "Token has expired."}), 401
        except JWTError:
            return jsonify({"error": "Invalid token."}), 401

        customer_id = payload.get("sub")
        if customer_id is None:
            return jsonify({"error": "Invalid token payload."}), 401

        kwargs["current_customer_id"] = int(customer_id)
        return view_func(*args, **kwargs)

    return wrapped
