from abc import ABC, abstractmethod


class RDFModule(ABC):
    def __init__(self, name, parser, logger, description="", displayname=None):
        self.name = name
        self.logger = logger
        self.parser = parser.add_parser(name.lower(), help=description)
        self.parser.set_defaults(func=self.handle)
        if displayname is None:
            self.displayname = name
        else:
            self.displayname = displayname

    @abstractmethod
    def handle(self, params, store=None):
        raise NotImplementedError()

    def log(self, msg, verbose=False):
        self.logger.out(f"{self.displayname}: {msg}", verbose, True)
