class ProjectNotFoundError(Exception):
    def __init__(self, msg):
        self.msg = msg


class ProcessNotFoundError(Exception):
    def __init__(self, msg):
        self.msg = msg
