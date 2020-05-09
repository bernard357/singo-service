from Flask import jsonify
import json
import logging
import werkzeug


logger = logging.getLogger(__name__)


class Handlers:
    ''' JSON errors are returned as {'code': 404, 'name': 'Not Found', 'description': '...'} '''

    def register_handlers(self, app):
        logger.debug(f"registering exception handlers...")
        app.register_error_handler(400, self.bad_request_error)
        app.register_error_handler(403, self.forbidden_error)
        app.register_error_handler(404, self.not_found_error)
        app.register_error_handler(500, self.internal_server_error)
        app.register_error_handler(werkzeug.exceptions.HTTPException, self.http_error)
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def bad_request_error(self, exception):
        message = str(exception.description) or 'Bad Request'
        logger.warning(f"ERROR 400 {message}")
        return jsonify(dict(code=400,
                            name='Bad Request',
                            description=message)), 400

    def forbidden_error(self, exception):
        message = str(exception.description) or 'Forbidden'
        logger.warning(f"ERROR 403 {message}")
        return jsonify(dict(code=403,
                            name='Forbidden',
                            description=message)), 403

    def not_found_error(self, exception):
        message = str(exception.description) or 'Not Found'
        logger.warning(f"ERROR 404 {message}")
        return jsonify(dict(code=404,
                            name='Not Found',
                            description=message)), 404

    def internal_server_error(self, exception):
        message = str(exception.description) or 'Internal Server Error'
        logger.warning(f"ERROR 500 {message}")
        return jsonify(dict(code=500,
                            name='Internal Server Error',
                            description=message)), 500

    def http_error(self, exception):  # return JSON instead of HTML for HTTP errors
        description = str(exception.description) or 'HTTP Error'
        logger.warning(f"ERROR {exception.code} {description}")
        response = exception.get_response()
        response.data = json.dumps(dict(code=exception.code,
                                        name=exception.name,
                                        description=description))
        response.content_type = "application/json"
        return response

    def before_request(self):
        pass

    def after_request(self, response):
        return response
