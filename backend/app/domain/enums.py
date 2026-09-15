from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @classmethod
    def allowed_transitions(
        cls,
    ) -> dict["RunStatus", set["RunStatus"]]:
        return {
            cls.QUEUED: {
                cls.RUNNING,
                cls.CANCELLED,
            },
            cls.RUNNING: {
                cls.COMPLETED,
                cls.FAILED,
                cls.CANCELLED,
            },
            cls.COMPLETED: set(),
            cls.FAILED: set(),
            cls.CANCELLED: set(),
        }

    def can_transition_to(
        self,
        target: "RunStatus",
    ) -> bool:
        return target in self.allowed_transitions().get(
            self,
            set(),
        )