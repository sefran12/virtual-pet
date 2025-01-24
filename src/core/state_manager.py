import json
from datetime import datetime
from typing import Any, Dict
from dataclasses import is_dataclass, asdict

class StateManager:
    def __init__(self):
        self._version = "1.1"
        self._state_history = []
        self._current_state = {}

    def snapshot(self, obj: Any) -> Dict:
        """Capture a serializable state snapshot of an object"""
        if is_dataclass(obj):
            state = asdict(obj)
        elif hasattr(obj, '__dict__'):
            state = vars(obj)
        else:
            state = dict(obj)
            
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'version': self._version,
            'state': state
        }
        self._state_history.append(snapshot)
        return snapshot

    def restore(self, snapshot: Dict) -> Any:
        """Restore object state from a snapshot (requires object-specific deserialization)"""
        if snapshot['version'] != self._version:
            raise ValueError(f"Snapshot version {snapshot['version']} does not match current {self._version}")
        return snapshot['state']

    def get_version_history(self):
        """Get complete state change history"""
        return self._state_history.copy()

    def serialize(self) -> str:
        """Serialize current state to JSON"""
        return json.dumps({
            'version': self._version,
            'history': self._state_history
        }, indent=2)

    @classmethod
    def deserialize(cls, data: str):
        """Deserialize from JSON string"""
        manager = cls()
        loaded = json.loads(data)
        manager._version = loaded['version']
        manager._state_history = loaded['history']
        return manager
