"""
Configuration loader for HAMLET.
Reads YAML files and exposes a clean Python API.
"""
from pathlib import Path
from typing import Dict, List, Any
import yaml

class ConfigLoader:
    """Loads YAML configuration files and provides easy access."""

    def __init__(self, config_dir: Path | str = None):
        if config_dir is None:
            # Default: <repo_root>/config/
            config_dir = Path(__file__).resolve().parents[2] / "config"
        self.config_dir = Path(config_dir)

        self.schemes_file = self.config_dir / "schemes.yaml"
        self.settings_file = self.config_dir / "settings.yaml"

        self._schemes_raw = self._load_yaml(self.schemes_file)
        self._settings = self._load_yaml(self.settings_file)

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    # ---------- Schemes API ----------
    def get_schemes(self) -> Dict[str, List[str]]:
        """
        Returns a flat dict {scheme_name: [prompts]} merging defaults
        and custom user-defined schemes.
        """
        flat: Dict[str, List[str]] = {}

        defaults = self._schemes_raw.get("default_schemes", {}) or {}
        customs = self._schemes_raw.get("custom_schemes", {}) or {}

        for name, body in {**defaults, **customs}.items():
            if isinstance(body, dict) and "prompts" in body:
                flat[name] = list(body["prompts"])
            elif isinstance(body, list):
                flat[name] = list(body)
        return flat

    def get_scheme_descriptions(self) -> Dict[str, str]:
        """Returns {scheme_name: description}."""
        out: Dict[str, str] = {}
        defaults = self._schemes_raw.get("default_schemes", {}) or {}
        customs = self._schemes_raw.get("custom_schemes", {}) or {}
        for name, body in {**defaults, **customs}.items():
            if isinstance(body, dict):
                out[name] = body.get("description", "")
            else:
                out[name] = ""
        return out

    # ---------- Settings API ----------
    @property
    def model_id(self) -> str:
        return self._settings.get("model", {}).get("id", "laion/clap-htsat-fused")

    @property
    def target_sr(self) -> int:
        return self._settings.get("model", {}).get("target_sample_rate", 48000)

    @property
    def default_window_sec(self) -> float:
        return self._settings.get("analysis", {}).get("default_window_sec", 6.0)

    @property
    def default_temperature(self) -> float:
        return self._settings.get("analysis", {}).get("default_temperature", 3.0)

    @property
    def min_chunk_ratio(self) -> float:
        return self._settings.get("analysis", {}).get("min_chunk_ratio", 1.0)

    @property
    def ui_settings(self) -> Dict[str, Any]:
        return self._settings.get("ui", {})
