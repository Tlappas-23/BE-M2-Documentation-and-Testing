from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from application.extensions import cache, db, limiter, ma
from config import Config

# Swagger configuration
SWAGGER_URL = '/api/docs'  # URL where I can view my documentation
API_URL = '/static/swagger.yaml'  # Where my swagger.yaml file lives

# Creating the Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop API"
    }
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    from application.blueprints.customer import customer_bp
    from application.blueprints.mechanic import mechanic_bp
    from application.blueprints.service_ticket import service_ticket_bp
    from application.blueprints.inventory import inventory_bp

    app.register_blueprint(customer_bp, url_prefix="/customers")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics")
    app.register_blueprint(service_ticket_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)  # Register Swagger UI

    with app.app_context():
        db.create_all()

    return app
