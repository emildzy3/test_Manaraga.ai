from pathlib import Path
from fastapi.templating import Jinja2Templates


def get_jinja2_templates(base_dir: Path) -> Jinja2Templates:
    templates_dir = base_dir / "templates"
    templates_dir.mkdir(exist_ok=True)
    return Jinja2Templates(directory=str(templates_dir))
