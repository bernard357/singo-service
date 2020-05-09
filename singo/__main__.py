import os

from api import app


host_binding = os.environ.get('SINGO_ADDRESS', '0.0.0.0')
host_port = os.environ.get('SINGO_PORT', '5000')
app.run(host=host_binding, port=int(host_port))
