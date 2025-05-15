
from dataclasses import dataclass, field
import os, uuid, socket

@dataclass
class Ctx:
    env: str = os.getenv("ENV", "dev")
    notes_folder: str = os.getenv("NOTES_FOLDER", "")
    output_folder: str = os.getenv("OUTPUT_FOLDER", "output")
    dry_run: bool = False
    trigger: str = os.getenv("TRIGGER", "manual")
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hostname: str = socket.gethostname()
    app_name: str = "obsidian-to-json"

    _CURRENT = None

    def activate(self):
        Ctx._CURRENT = self
        os.environ.update({
            "ENV": self.env,
            "TRIGGER": self.trigger,
            "EXECUTION_ID": self.execution_id,
            "NOTES_FOLDER": self.notes_folder,
            "OUTPUT_FOLDER": self.output_folder,
        })
        os.makedirs(self.output_folder, exist_ok=True)

    @classmethod
    def current(cls):
        if cls._CURRENT is None:
            cls._CURRENT = Ctx()
            cls._CURRENT.activate()
        return cls._CURRENT
