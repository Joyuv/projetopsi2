from flask import *

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route('/login' methods=['POST', 'GET'])
    return "Nada"
