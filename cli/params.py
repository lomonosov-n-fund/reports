import click
from pathlib import Path
from datetime import datetime, date

def common_options(func):
    """Decorator with shared CLI options"""
    func = click.option("--dry-run", is_flag=True, help="Preview without saving")(func)
    func = click.option("--quarter", type=int, help="Quarter (1-4)")(func)
    func = click.option("--year", type=int, help="Reporting year")(func)
    func = click.option("--output-dir", default="./outputs", type=Path, help="Output directory")(func)
    func = click.option("--verbose", is_flag=True, help="Show detailed output")(func)
    func = click.option("--operator", is_flag=True, help="Show console output")(func)
    func = click.option("--latex", is_flag=True, help="Generate LaTeX files")(func)
    return func

