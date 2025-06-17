from flask import Flask
from flask_cors import CORS
from api.routes.checkout import checkout_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(checkout_bp)

if __name__ == '__main__':
    app.run(debug=True) 