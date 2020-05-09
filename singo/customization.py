import os


class Customization:

    def __init__(self):
        self.state_file = os.environ.get('STATE_FILE', 'fixtures/state.yaml')
        self.commands_file = os.environ.get('COMMANDS_FILE', 'fixtures/commands.yaml')


c11n = Customization()
