"""Command line for sites that use the ISCC theme.

zensical-iscc build      build the site with Zensical, then publish its Markdown pages
zensical-iscc markdown   publish the Markdown pages into an already built site
zensical-iscc check      check the configuration and the built site
"""

import argparse
import subprocess
import sys
from pathlib import Path

from zensical_iscc import check, markdown, project

COMMANDS = ("build", "markdown", "check")


def parse_args(argv):
    # type: (list[str] | None) -> argparse.Namespace
    """Parse the command line."""
    description, epilog = str(__doc__).split("\n\n", 1)
    parser = argparse.ArgumentParser(
        prog="zensical-iscc",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("-f", "--config-file", default="zensical.toml", type=Path, help="default: zensical.toml")
    parser.add_argument("--strict", action="store_true", help="check: fail on warnings as well as errors")
    return parser.parse_args(argv)


def run_build(config_path):
    # type: (Path) -> int
    """Build the site with Zensical, then publish its Markdown pages."""
    command = [sys.executable, "-m", "zensical", "build", "--clean", "--config-file", str(config_path)]
    return subprocess.run(command, check=False).returncode or run_markdown(config_path)  # noqa: S603


def run_markdown(config_path):
    # type: (Path) -> int
    """Write the Markdown copies of all pages and `llms-full.txt` into the built site."""
    config = project.load_project(config_path)
    built_dir = project.site_dir(config_path, config)
    if not built_dir.is_dir():
        print(f"site directory not found: {built_dir} (build the site first)", file=sys.stderr)
        return 1
    docs_dir = project.docs_dir(config_path, config)
    found = markdown.page_sources(docs_dir, project.custom_dir(config_path, config))
    sources = markdown.ordered_sources(found, config.get("nav", []))
    markdown.write_pages(docs_dir, built_dir, sources)
    print(f"wrote {len(sources)} Markdown pages and llms-full.txt to {built_dir}")
    return 0


def run_check(config_path, strict):
    # type: (Path, bool) -> int
    """Print the findings for the site and return 1 if any of them fails the check."""
    findings = check.check(config_path)
    for level, message in findings:
        print(f"{level}: {message}")
    errors = sum(level == "error" for level, _ in findings)
    warnings = len(findings) - errors
    print(f"{errors} errors, {warnings} warnings")
    return int(errors > 0 or (strict and warnings > 0))


def main(argv=None):
    # type: (list[str] | None) -> int
    """Run a theme command and return its exit status."""
    args = parse_args(argv)
    if not args.config_file.is_file():
        print(f"configuration file not found: {args.config_file}", file=sys.stderr)
        return 1
    if args.command == "build":
        return run_build(args.config_file)
    if args.command == "markdown":
        return run_markdown(args.config_file)
    return run_check(args.config_file, args.strict)
