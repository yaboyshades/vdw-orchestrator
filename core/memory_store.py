import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

class MemoryStore:
    """Simple file-based Atoms & Bonds memory.
    Atoms are stored as JSON files; bonds tracked in an adjacency list.
    """

    def __init__(self, base_dir: str = "data/memory"):
        self.base = Path(base_dir)
        self.atoms = self.base / "atoms"
        self.bonds = self.base / "bonds.json"
        self.atoms.mkdir(parents=True, exist_ok=True)
        self.bonds.parent.mkdir(parents=True, exist_ok=True)
        if not self.bonds.exists():
            self.bonds.write_text(json.dumps({}))
        self.logger = logging.getLogger(self.__class__.__name__)

    async def store_atom(self, atom_id: str, content: Dict[str, Any]):
        # Custom JSON encoder to handle datetime objects
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        (self.atoms / f"{atom_id}.json").write_text(json.dumps(content, indent=2, default=json_serial))

    async def get_atom(self, atom_id: str) -> Optional[Dict[str, Any]]:
        p = self.atoms / f"{atom_id}.json"
        if not p.exists():
            return None
        return json.loads(p.read_text())

    async def link(self, from_id: str, to_id: str, relation: str):
        bonds = json.loads(self.bonds.read_text())
        bonds.setdefault(from_id, []).append({"to": to_id, "relation": relation})
        self.bonds.write_text(json.dumps(bonds, indent=2))

    async def neighbors(self, atom_id: str) -> List[Dict[str, str]]:
        bonds = json.loads(self.bonds.read_text())
        return bonds.get(atom_id, [])
