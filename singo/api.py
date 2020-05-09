from Flask import Flask
from flask_cors import CORS
import logging


from api_channel import Channel
from api_handlers import Handlers
from api_identities import Identities
from api_maintenance import Maintenance
from permissions import Permissions
from customization import c11n
from commands import Commands


logging.basicConfig(format='%(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
cors = CORS(app)

# WIP: Dockerfile optimised https://blog.realkinetic.com/building-minimal-docker-containers-for-python-applications-37d0272c52f3
# WIP: deploy on AWS with zappa

permissions = Permissions(path='fixtures/permissions.yaml')

identities = Identities(permissions=permissions)
identities.register_routes(app)

channels = {k: Channel(name=k, permissions=permissions) for k in ['universe', 'community', 'board', 'item']}
for _, channel in channels.items():
    channel.register_routes(app, wrapper=identities.inject_identity)

maintenance = Maintenance(permissions=permissions,
                          users=identities.store,
                          channels=channels,
                          state_file=c11n.state_file)
maintenance.register_routes(app, wrapper=identities.inject_identity)

handlers = Handlers()
handlers.register_handlers(app)

commands = Commands()
identities.emitter = commands.emit
for _, channel in channels.items():
    channel.emitter = commands.emit
