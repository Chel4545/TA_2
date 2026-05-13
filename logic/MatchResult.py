from dataclasses import dataclass, field


@dataclass
class MatchResult:
    start: int
    end: int
    value: str
    groups: dict[int, str] = field(default_factory=dict)

    # .group()
    def group(self, num: int = 0) -> str | None:
        if num == 0:
            return self.value
        return self.groups.get(num)

    # []
    def __getitem__(self, num: int) -> str | None:
        return self.group(num)

    # iter
    def __iter__(self):
        for num in sorted(self.groups):
            yield self.groups[num]