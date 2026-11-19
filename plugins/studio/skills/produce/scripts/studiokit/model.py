"""Storyboard data model. No Pillow needed."""
from dataclasses import dataclass, field
from pathlib import Path

SCENE_TYPES = ("title", "bullets", "stat", "compare", "quote", "image", "cta")


@dataclass
class Scene:
    index: int
    type: str
    duration: float
    theme: str
    accent: tuple
    transition: str
    text: str = ""
    items: list = field(default_factory=list)
    value: float = 0
    label: str = ""
    prefix: str = ""
    suffix: str = ""
    left: dict = field(default_factory=dict)
    right: dict = field(default_factory=dict)
    author: str = ""
    sub: str = ""
    image: Path | None = None
    start: float = 0.0

    def visible_text(self) -> list[str]:
        """Every text string shown on this scene (used for word counts and captions)."""
        t = self.type
        if t == "stat":
            return [f"{self.prefix}{self.value:g}{self.suffix}", self.label]
        if t == "compare":
            return [self.left["title"], *self.left["items"], self.right["title"], *self.right["items"]]
        return [s for s in [self.text, *self.items, self.author, self.sub] if s]

    def words(self) -> int:
        return sum(len(s.split()) for s in self.visible_text())


@dataclass
class Storyboard:
    title: str
    scenes: list
    audio: Path | None = None
    meta: dict = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return sum(s.duration for s in self.scenes)


class SpecError(ValueError):
    pass


def default_duration(kind: str, words: int, n_items: int) -> float:
    base = {"stat": 3.0, "compare": 4.5, "image": 3.5, "cta": 3.0}.get(kind)
    if kind == "bullets":
        return 1.5 + 1.0 * n_items
    return base if base else max(2.0, round(1.2 + 0.4 * words, 1))
