from event_generator import Event


class EnviromentInfo:
    def __init__(self, log: dict[Event, dict[int, int]], public_resources: dict):
        self.log: dict[Event, dict[int, int]] = log
        self.public_resources = public_resources

    def __str__(self) -> str:
        return f"Log: {self.log}, Public resources: {self.public_resources}"

    def __repr__(self) -> str:
        return str(self)
