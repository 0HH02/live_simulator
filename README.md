## Presentation

The simulation project focuses on creating a virtual environment where autonomous agents interact with each other and their surroundings, making decisions that affect their survival. A series of game mechanics based on the prisoner's dilemma are used to model interactions and events that impact the agents. This study investigates which behaviors allow agents and their groups to survive longer, how environmental conditions influence these decisions, and the impact of offspring on the adaptability of societies.

### Simulation Objective

The primary objective of this simulation is to analyze the behavior in society of individuals who must decide whether to cooperate or not in the face of various social and natural phenomena, with the goal of surviving as long as possible. The specific questions this study seeks to answer are:

1. What behaviors allow the group to survive the longest?
2. What behaviors allow an individual to survive the longest?
3. Is the thief the one who survives the longest?
4. How do agents change in more adverse or favorable environments?
5. Does offspring make societies more easily adaptable to environmental changes?

### Game Mechanics

In each turn of the simulation, players lose a fixed amount of resources. Each player has access to the history of moves made by other participants, allowing them to know who cooperated and who did not in past collaborative events. Participants, the number of participants, the type of event, and the amount of resources at stake are selected randomly. Players face a prisoner's dilemma to divide resources, and the results are interpreted according to the type of event.

#### Types of Events

1. **Special Events**: These can be either beneficial or harmful and affect one or more people. Example: Fulano, Mengano, and Sultano lose/gain X amount of resources.
2. **Collaborative Events**: These can involve gaining or losing an X amount of unlocked resources. Positive example: 300 resources are found to share, but participants must dig for a whole day. Negative example: A natural disaster affects the village, requiring 300 resources for repairs.

### System Operation

An event generator creates an event type based on a predefined distribution, selects the players, determines the amount of resources at stake, and alters the environment according to the game results. At the end of each day, the process repeats.

### System Classes

The following describes the main classes used in the simulation:

#### Agent (ABC)

```python
from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def Action(self, env_info, event):
        pass
```

#### Environment

```python
class Environment:
    def GetEnvironmentFrom(self, agent):
        return EnviromentInfo()

    def __init__(self):
        self.resource = {}
        self.day = 0
        self.log = {}

    resource: dict[Agent, int]
    day: int
    log: dict[Event, dict[Agent, Action]]
```

#### Action (Enum)

```python
from enum import Enum

class Action(Enum):
    COOP = "Cooperate"
    EXPLOIT = "Exploit"
    INACT = "Inaction"
```

#### EnvironmentInfo

```python
class EnvironmentInfo:
    def __init__(self):
        self.log = {}
        self.public_resource = {}

    log: dict[Event, dict[Agent, Action]]
    public_resource: dict[Agent, int]
```

#### EventGenerator (ABC)

```python
from abc import ABC, abstractmethod

class EventGenerator(ABC):
    @abstractmethod
    def GetNewEvent(self, env_info):
        pass
```

## Conclusions

This simulation project provides a robust platform for exploring cooperative and non-cooperative behavior in social and natural contexts. By implementing various game mechanics and generating random events, it is possible to observe how different strategies impact the survival of individuals and groups. The results obtained can offer valuable insights into the dynamics of cooperation and competition in adverse and favorable environments, as well as the influence of offspring on the adaptability of societies.