class ProjectNotFoundError(Exception):
    def __init__(self, msg):
        self.msg = msg


class CollectionNotFoundError(Exception):
    def __init__(self, msg):
        self.msg = msg


class ProcessNotFoundError(Exception):
    def __init__(self, msg):
        self.msg = msg


class ContainerRunError(Exception):
    def __init__(self, msg):
        self.msg = msg
