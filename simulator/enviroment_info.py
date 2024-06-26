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
        self,
        day: int,
        lost_per_day: int,
        public_resources: dict,
    ) -> None:
        self.day: int = day
        self.lost_per_day: int = lost_per_day
        self.public_resources: dict = public_resources

    def __str__(self) -> str:
        return f"Day: {self.day}\nLost per day: {self.lost_per_day}\nPublic resources: {self.public_resources}"

    def __repr__(self) -> str:
        return str(self)
