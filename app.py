from flask import Flask

app = Flask(__name__)

import config
import routes
import models
import api

if __name__ == "__main__":
    app.run(debug=True)