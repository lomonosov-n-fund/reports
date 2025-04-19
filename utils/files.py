from pathlib import Path
import click

def ensure_writable_dir(path: Path, dry_run: bool = False) -> None:
    """Validates or creates output directory."""
    if dry_run:
        return
        
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".permission_test"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        raise click.ClickException(
            f"Output directory error: {e}\n"
            f"Try: mkdir -p {path} && chmod +w {path}"
        )