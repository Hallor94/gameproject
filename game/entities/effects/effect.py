# file: entities/effects/effect.py

class Effect:
    def __init__(
        self,
        id,
        name,
        description="",
        icon=None,
        duration=None,
        modifiers=None,
        per_turn=False,
        tags=None,
        source=None,
        stackable=False,
        conditions=None,
        allow_enemy=True
    ):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon  # filename like 'adrenaline.png'
        self.duration = duration
        self.remaining_duration = duration  # tracks countdown
        self.modifiers = modifiers or {}
        self.per_turn = per_turn
        self.tags = tags or []
        self.source = source  # e.g. "Starting Boost" or entity.name
        self.stackable = stackable
        self.conditions = conditions or {}
        self.allow_enemy = allow_enemy

    def tick(self):
        if self.remaining_duration is not None and self.remaining_duration > 0:
            self.remaining_duration -= 1

    def is_expired(self):
        return self.remaining_duration is not None and self.remaining_duration <= 0


    def copy(self):
        """Create a copy when applying to an entity to avoid shared state."""
        return Effect(
            id=self.id,
            name=self.name,
            description=self.description,
            icon=self.icon,
            duration=self.duration,
            modifiers=self.modifiers.copy(),
            per_turn=self.per_turn,
            tags=self.tags[:],
            source=self.source,
            stackable=self.stackable
        )


    def __repr__(self):
        return f"<Effect {self.id} ({self.name}) x{'∞' if self.duration is None else self.remaining_duration}>"

