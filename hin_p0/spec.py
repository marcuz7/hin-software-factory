"""Minimal requirement traceability scaffold; not a full specification compiler."""
from pathlib import Path

OUTPUTS = ("API_CONTRACTS.md", "DB_MIGRATIONS.md", "UI_SPEC.md", "WORK_PACKAGES.md")

def scaffold(source_path, output_dir):
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError(source)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    for filename in OUTPUTS:
        path = target / filename
        if path.exists():
            raise FileExistsError(f"will not overwrite: {path}")
        path.write_text(
            f"# {filename.removesuffix('.md').replace('_', ' ')}\n\n"
            f"Source: {source.name}\n\n"
            "Status: SCAFFOLD ONLY — requires architect review and source-linked requirements.\n",
            encoding="utf-8")
    return list(OUTPUTS)
