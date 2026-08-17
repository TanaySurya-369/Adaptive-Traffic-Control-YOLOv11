from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UniqueTrackCounter:
    """Tracks unique detection IDs per lane to prevent double counting."""

    seen: dict[int, set[int | str]] = field(default_factory=dict)

    def mark_seen(self, lane_id: int, object_id: int | str) -> bool:
        lane_seen = self.seen.setdefault(lane_id, set())
        if object_id in lane_seen:
            return False
        lane_seen.add(object_id)
        return True
