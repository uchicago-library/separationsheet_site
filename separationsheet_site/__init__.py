from flask import Flask, jsonify
from flask_pymongo import PyMongo
from .blueprint import BLUEPRINT, __version__, __email__, __author__
from .blueprint.exceptions import Error


app = Flask(__name__)

app.config["MONGO_DBNAME"] = "separationsheet"
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017"
app.config['WTF_CSRF_ENABLED'] = False

mongo = PyMongo(app)

@app.errorhandler(Error)
def handle_errors(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


app.register_blueprint(BLUEPRINT)
