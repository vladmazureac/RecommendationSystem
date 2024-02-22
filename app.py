from flask import Flask
from view import recommendation_blueprint

app = Flask(__name__)

# Înregistrarea blueprint-ului în aplicație
app.register_blueprint(recommendation_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
