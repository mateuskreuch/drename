from pathlib import Path
from replacer import CaseAwareReplacer, FileIsBinaryError
from rich import print
from rich.markup import escape
from rich_differ import rich_diff
from rich.live import Live
from rich.table import Table
import os, typer, subprocess

def get_all_paths_to_replace(path: Path):
    if path.is_file():
        return [path]

    file_objects: list[Path] = []

    for root_str, dir_names, file_names in os.walk(path):
        dir_names[:] = [d for d in dir_names if not d.startswith('.')]
        root_path = Path(root_str)
        file_objects += [root_path / f for f in file_names if not f.startswith('.')] \
                      + [root_path / d for d in dir_names]

    return file_objects

def is_git_clean(path: Path):
    if not path.is_dir():
        return True

    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True, capture_output=True, cwd=path
        )

        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True, capture_output=True, text=True, cwd=path
        )

        return not status_result.stdout

    except (subprocess.CalledProcessError, FileNotFoundError):
        return True

app = typer.Typer()

@app.command()
def drename(
    old: str,
    new: str,
    dry: bool = typer.Option(False, help="Perform a dry run without making changes"),
    force: bool = typer.Option(False, help="Force replacements even with pending git changes"),
    path: Path = typer.Argument(Path.cwd(), help="Root directory or file to process")
):
    """
    Replace OLD with NEW in file names, directories, and file contents while respecting case:\n
    \n
        OLD = test/my/user | NEW = wow/very/nice\n
    \n
    Will replace, for example:\n
    \n
        test_My_USER -> wow_Very_NICE\n
        test-_my-user -> wow-_very-nice\n
        testMyUser -> wowVeryNice\n
        TEST_MY_USER -> WOW_VERY_NICE\n
    """
    if old == new:
        print("[red]Old and new are the same. No actions will be taken.[/]")
        raise typer.Exit(code=1)

    if not force and not dry and not is_git_clean(path):
        print("[red]There are pending git changes. Please commit or stash them first.[/]")
        print("[yellow]To override, run with --force[/]")
        raise typer.Exit(code=1)

    replacer = CaseAwareReplacer(old, new, dry_run=dry)
    paths = get_all_paths_to_replace(path)

    table = Table()
    table.add_column("Type")
    table.add_column("Path")
    table.add_column("Errors")

    with Live(table, auto_refresh=False) as live:
        for old_path, new_path in replacer.iter_replace_paths(paths):
            relative_old_path = old_path.relative_to(path)
            relative_new_path = new_path.relative_to(path)
            type_text = ""
            errors = []

            try:
                replacer.replace_file_contents(old_path)
                type_text = "[yellow]File[/]"

            except IsADirectoryError:
                type_text = "[bright_black]Directory[/]"

            except FileIsBinaryError:
                type_text = "[bright_black]File (binary)[/]"

            except AssertionError as e:
                type_text = "[bright_black]File[/]"

                if str(e):
                    errors.append(str(e))

            try:
                replacer.rename_file(old_path)

            except FileExistsError:
                errors.append(f"{relative_new_path} (conflict)")

            except OSError:
                errors.append("OS failed")

            table.add_row(
                type_text,
                rich_diff(escape(str(relative_old_path)), escape(str(relative_new_path))),
                "[red]" + "; ".join(errors) + "[/]"
            )
            live.update(table)

    replacements_made = replacer.get_replacements_made().items()

    if replacements_made:
        table = Table()
        table.add_column("Old")
        table.add_column("New")

        for old_str, new_str in replacements_made:
            table.add_row(old_str, new_str)

        print(table)

    else:
        print("[red]No possible replacements found.[/]")

if __name__ == "__main__":
    app()