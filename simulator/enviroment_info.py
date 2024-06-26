from .event_generator import Event
from .utils import Action


class EnviromentInfo:
    """
    Represents the environment information for the simulator.

    Attributes:
        log (dict[Event, dict[int, Action]]): A dictionary that maps each events to a dictionary that maps each agent to the actions that he made in that event.

        public_resources (dict[int, int]): A dictionary that represents the public resources available of each agent.
    """

    def __init__(
        self, log: dict[Event, dict[int, Action]], public_resources: dict[int, int]
    ):
        self.log: dict[Event, dict[int, Action]] = log
        self.public_resources: dict[int, int] = public_resources

    def __str__(self) -> str:
        return f"Log: {self.log}, Public resources: {self.public_resources}"

    def __repr__(self) -> str:
        return str(self)
