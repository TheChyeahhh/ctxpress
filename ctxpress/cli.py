from __future__ import annotations

import os
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from dotenv import load_dotenv

from .compressor import build_prompt, CompressionResult, estimate_tokens, LEVELS
from .ai import compress

load_dotenv()
console = Console()

MAX_INPUT_CHARS = 80_000


def print_stats(result: CompressionResult) -> None:
    orig_tokens = estimate_tokens(result.original_chars * " ")
    comp_tokens = estimate_tokens(result.compressed_chars * " ")

    table = Table(box=None, pad_edge=False, show_header=False)
    table.add_column("metric", style="dim", width=22)
    table.add_column("value")

    bar_full = 20
    filled = max(1, round(result.ratio * bar_full))
    bar = "█" * filled + "░" * (bar_full - filled)
    color = "green" if result.saved_pct >= 50 else "yellow" if result.saved_pct >= 25 else "dim"

    table.add_row("Level", result.level.upper())
    table.add_row("Original", f"{result.original_chars:,} chars  (~{estimate_tokens(result.original_chars * ' '):,} tokens)")
    table.add_row("Compressed", f"{result.compressed_chars:,} chars  (~{estimate_tokens(result.compressed_chars * ' '):,} tokens)")
    table.add_row("Ratio", f"[{color}]{bar}  {result.saved_pct}% smaller[/{color}]")

    console.print(Panel(table, title="[bold cyan]Compression Stats[/bold cyan]",
                        border_style="cyan", padding=(1, 2)))
    console.print()


@click.command()
@click.argument("inputfile", required=False, type=click.Path(exists=True, readable=True))
@click.option("--level", "-l", default="medium",
              type=click.Choice(["light", "medium", "heavy"], case_sensitive=False),
              help="Compression level. Default: medium.")
@click.option("--output", "-o", default=None,
              type=click.Path(),
              help="Write compressed output to a file instead of stdout.")
@click.option("--stats-only", is_flag=True, default=False,
              help="Show stats panel without printing the compressed text.")
@click.option("--backend", "-b", default=None,
              type=click.Choice(["claude", "openai"], case_sensitive=False),
              help="AI backend. Defaults to AI_BACKEND env var or claude.")
def main(inputfile: str | None, level: str, output: str | None,
         stats_only: bool, backend: str | None) -> None:
    """Loss-aware context compression — shrink any text while keeping what matters.

    \b
    Three ways to use ctxpress:

      1. Compress a file:
         ctxpress document.txt
         ctxpress document.txt --level heavy --output compressed.txt

      2. Pipe input:
         cat long_doc.txt | ctxpress
         cat meeting_notes.txt | ctxpress --level light

      3. Interactive paste (no args):
         ctxpress
         [paste text, then Ctrl+D (Mac/Linux) or Ctrl+Z+Enter (Windows)]

    \b
    Compression levels:
      light   Keep ~70%  — remove filler and redundancy
      medium  Keep ~40%  — extract key points, summarize verbose sections
      heavy   Keep ~15%  — bullet-point extraction, maximum compression
    """
    selected_backend = backend or os.getenv("AI_BACKEND", "claude").lower()

    # Get input
    if inputfile:
        text = Path(inputfile).read_text(encoding="utf-8", errors="replace")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        console.print()
        console.print(Panel(
            "[bold]Paste your text below.[/bold]\n\n"
            "Press [bold cyan]Ctrl+D[/bold cyan] (Mac/Linux) or "
            "[bold cyan]Ctrl+Z + Enter[/bold cyan] (Windows) when done.",
            border_style="dim", padding=(1, 2),
        ))
        console.print()
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        text = "\n".join(lines)

    text = text.strip()
    if not text:
        console.print("[bold red]Error:[/bold red] No input text provided.")
        sys.exit(1)

    if len(text) > MAX_INPUT_CHARS:
        console.print(
            f"[yellow]Input truncated to {MAX_INPUT_CHARS:,} chars "
            f"(was {len(text):,}).[/yellow]"
        )
        text = text[:MAX_INPUT_CHARS]

    config = LEVELS[level.lower()]

    console.print()
    console.print(Rule("[dim]ctxpress[/dim]"))
    console.print(f"  [dim]Level:[/dim]    {level.upper()} — {config['description'][:60]}...")
    console.print(f"  [dim]Input:[/dim]    {len(text):,} chars (~{estimate_tokens(text):,} tokens)")
    console.print(f"  [dim]Target:[/dim]   ~{config['target_pct']}% of original")
    console.print(f"  [dim]Backend:[/dim]  {selected_backend}")
    console.print()

    prompt = build_prompt(text, level.lower())

    with console.status("[bold green]Compressing...[/bold green]"):
        try:
            compressed = compress(prompt, selected_backend)
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
            sys.exit(1)

    result = CompressionResult(
        compressed=compressed,
        original_chars=len(text),
        compressed_chars=len(compressed),
        ratio=len(compressed) / max(1, len(text)),
        level=level.lower(),
    )

    # Stats
    print_stats(result)

    # Output
    if output:
        Path(output).write_text(compressed, encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] Written to: {output}\n")
    elif not stats_only:
        console.print(Panel(
            Text(compressed),
            title="[bold cyan]Compressed Output[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        ))
        console.print()


if __name__ == "__main__":
    main()
