from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: str
    template: str

    def render(self, **values: str) -> str:
        return self.template.format(**values)


def load_prompt_template(template_key: str, yaml_path: Path | None = None) -> PromptTemplate:
    if yaml_path is None:
        yaml_path = Path(__file__).parent / "prompt_templates.yaml"

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if template_key not in data:
        raise KeyError(f"Prompt template '{template_key}' not found in {yaml_path}")

    config = data[template_key]
    return PromptTemplate(
        name=config["name"],
        version=config["version"],
        template=config["template"].strip(),
    )


TICKET_SUMMARY_V1 = load_prompt_template("ticket_summary_v1")
