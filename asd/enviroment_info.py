class EnviromentInfo:
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
