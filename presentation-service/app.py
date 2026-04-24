from flask import Flask, request, render_template_string
import requests
# import necessary dependencies

# Initialization: Create the Flask instance
app = Flask(__name__)

DATA_SERVICE = "http://47.93.33.52:5000"
WORKFLOW = "http://47.93.33.52:5001"
# The other two containers' access port

HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Poster Submission System</title>

<style>
body{
    font-family:Arial;
    background:#f4f6f8;
    padding:40px;
}
.box{
    max-width:800px;
    margin:auto;
    background:white;
    padding:30px;
    border-radius:12px;
    box-shadow:0 0 20px rgba(0,0,0,.08);
}
input,textarea{
    width:100%;
    padding:12px;
    margin-top:8px;
    margin-bottom:18px;
    border:1px solid #ddd;
    border-radius:8px;
}
button{
    background:#ff6600;
    color:white;
    border:none;
    padding:12px 24px;
    border-radius:8px;
    cursor:pointer;
}
img{
    max-width:300px;
    margin-top:15px;
    border-radius:8px;
}

.tag{
    display:inline-block;
    padding:8px 14px;
    border-radius:20px;
    font-weight:bold;
    margin-bottom:10px;
}

.ready{background:#d4f7d4;color:#137913;}
.revision{background:#fff1cc;color:#9b6b00;}
.incomplete{background:#ffd6d6;color:#b30000;}
.pending{background:#e0e0e0;color:#333;}
</style>
</head>

<body>
<div class="box">

<h1>Poster Submission System</h1>

<form method="POST" enctype="multipart/form-data">

<label>Title</label>
<input type="text" name="title">

<label>Description</label>
<textarea name="desc" ></textarea>

<label>Image</label>
<input type="file" name="file" accept="image/png, image/jpeg">

<button type="submit">Submit</button>

</form>

{% if result %}
<hr>

<h2>Result</h2>

<div id="statusBox" class="tag pending">PENDING</div>

<p><b>ID:</b> {{ result.id }}</p>
<p><b>Title:</b> {{ result.title }}</p>
<p><b>Description:</b> {{ result.description }}</p>

<p><b>Filename:</b> {{ result.filename }}</p>

<p><b>Status Detail:</b> <span id="statusDetail">Loading...</span></p>

{% if result.image_url %}
<img src="{{ result.image_url }}">
{% endif %}

{% endif %}

</div>

{% if result %}

<script>
const submissionId = "{{ result.id }}";

window.pollingTimer = setInterval(fetchStatus, 2000);

fetchStatus();

async function fetchStatus(){
    try{
        const res = await fetch("/check/" + submissionId);

        // A 404 error or error will directly stop the polling
        if (!res.ok) {
            if (res.status === 404) {
                clearInterval(window.pollingTimer);
            }
            return;
        }

        const data = await res.json();

        const box = document.getElementById("statusBox");
        const detail = document.getElementById("statusDetail");

        const status = data.status || "PENDING";

        box.innerText = status;
        detail.innerText = data.status_detail || "No detail";

        box.className = "tag " + (
            status === "READY" ? "ready" :
            status === "NEEDS REVISION" ? "revision" :
            status === "INCOMPLETE" ? "incomplete" :
            "pending"
        );

        // READY stop polling
        if (status === "READY") {
            clearInterval(window.pollingTimer);
        }

    } catch(e){
        console.log(e);
    }
}
</script>

{% endif %}

</body>
</html>
"""
# Core logic of the code above:
# 1. Switch the background color based on different labels
# .ready{background:#d4f7d4;color:#137913;}
# .revision{background:#fff1cc;color:#9b6b00;}
# .incomplete{background:#ffd6d6;color:#b30000;}
# .pending{background:#e0e0e0;color:#333;}

# 2. The variable that stores the ID from the backend for later on API Query
# const submissionId = "{{ result.id }}";

# 3. Obtain the state check result from the backend in an asynchronous manner.

# 4. Polling for dynamic update.
# setInterval(fetchStatus, 2000);


@app.route("/", methods=["GET", "POST"])
# Method allowed: GET & POST
def index():
    result = None

    # submission analysis: get corresponding information
    if request.method == "POST":
        title = request.form.get("title", "")
        desc = request.form.get("desc", "")
        file = request.files.get("file")

        image_url = ""
        filename = ""

        # NEW: capture filename
        if file and file.filename:
            filename = file.filename

        # Stream Upload: Upload the file to DATA_SERVICE.
        if file and file.filename:
            up = requests.post(
                DATA_SERVICE + "/upload",
                files={"file": (file.filename, file.stream, file.mimetype)},
                timeout=10
            )

            print("UPLOAD RESPONSE:", up.text)
            image_url = up.json().get("url", "")

        # Workflow Submit
        wf = requests.post(
            WORKFLOW + "/submit",
            json={
                "title": title,
                "description": desc,
                "image_url": image_url,
                "filename": filename
            },
            timeout=10
        )

        wf_json = wf.json()
        sid = wf_json["id"]

        result = {
            "id": sid,
            "title": title,
            "description": desc,
            "image_url": image_url,
            "filename": filename
        }

    return render_template_string(HTML, result=result)


@app.route("/check/<id>")
def check(id):
    res = requests.get(f"{DATA_SERVICE}/submissions/{id}")
    return res.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)