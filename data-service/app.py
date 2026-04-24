from flask import Flask, request
from dotenv import load_dotenv
import sqlite3
import oss2
import os
import uuid
import imghdr

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Retrieve OSS credentials from environment variables
ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
BUCKET_NAME = os.getenv("OSS_BUCKET")
ENDPOINT = os.getenv("OSS_ENDPOINT")

# Ensure all required OSS configurations are present
if not all([ACCESS_KEY_ID, ACCESS_KEY_SECRET, BUCKET_NAME, ENDPOINT]):
    raise Exception("Missing OSS environment variables")

# Initialize OSS client
auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)


# Establish SQLite database connection
def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create submission table if it does not exist
def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS submission (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        image_url TEXT,
        filename TEXT,
        status TEXT,
        status_detail TEXT
    )
    """)
    conn.commit()
    conn.close()


# Initialize database when application starts
with app.app_context():
    init_db()


# File upload endpoint (image-only with strict validation)
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "no file provided"}, 400

    file = request.files["file"]

    if file.filename == "":
        return {"error": "empty filename"}, 400

    try:
        filename = file.filename.lower()

        # ===== 1. Check extension =====
        if "." not in filename:
            return {"error": "invalid file name"}, 400

        ext = filename.rsplit(".", 1)[-1]
        ALLOWED_EXT = {"jpg", "jpeg", "png"}

        if ext not in ALLOWED_EXT:
            return {"error": "only image files (jpg/jpeg/png) are allowed"}, 400

        # ===== 2. Check MIME type =====
        ALLOWED_MIME = {"image/jpeg", "image/png"}

        if file.mimetype not in ALLOWED_MIME:
            return {"error": "invalid file type"}, 400

        # ===== 3. Read file content =====
        file_bytes = file.read()

        # ===== 4. (Optional but recommended) Check real file content =====
        import imghdr
        file_type = imghdr.what(None, file_bytes)

        if file_type not in ["jpeg", "png"]:
            return {"error": "file content is not a valid image"}, 400

        # ===== 5. Generate filename =====
        new_name = f"{uuid.uuid4()}.{ext}"

        # ===== 6. Upload =====
        bucket.put_object(new_name, file_bytes)

        url = f"https://{BUCKET_NAME}.{ENDPOINT}/{new_name}"

        return {"url": url}

    except Exception as e:
        return {"error": str(e)}, 500


# Create a new submission record
@app.route("/submissions", methods=["POST"])
def create():
    data = request.json

    conn = get_db()
    conn.execute(
        "INSERT INTO submission VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data["id"],
            data["title"],
            data["description"],
            data["image_url"],
            data.get("filename", ""),
            data["status"],
            data.get("status_detail", "")
        )
    )
    conn.commit()
    conn.close()

    return {"message": "created"}


# Retrieve a submission by ID
@app.route("/submissions/<id>", methods=["GET"])
def get_one(id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM submission WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    if not row:
        return {"error": "not found"}, 404

    return dict(row)


# Update submission status
@app.route("/submissions/<id>", methods=["PUT"])
def update(id):
    data = request.json

    conn = get_db()

    conn.execute(
        "UPDATE submission SET status=?, status_detail=? WHERE id=?",
        (
            data["status"],
            data.get("status_detail", ""),
            id
        )
    )

    conn.commit()
    conn.close()

    return {"message": "updated"}


# Start Flask application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)