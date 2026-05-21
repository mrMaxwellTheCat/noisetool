from __future__ import annotations

import argparse

SHELL_COMPLETION_SCRIPT = """
_noisetool_completion() {
    local cur prev words cword
    _init_completion || return

    local opts="--type -t --duration -d --sample-rate -r --mono --stereo --output-dir -o --format -f --bit-depth --lufs --measure --peak --seed --list --version --verbose -v --log-file --no-banner --help -h --generate-completion --config --example-config"

    case $prev in
        --type|-t)
            COMPREPLY=($(compgen -W "all white pink brown blue violet grey" -- "$cur"))
            return
            ;;
        --format|-f)
            COMPREPLY=($(compgen -W "all wav flac" -- "$cur"))
            return
            ;;
        --bit-depth)
            COMPREPLY=($(compgen -W "16 24 32" -- "$cur"))
            return
            ;;
        --config|--log-file|--example-config)
            COMPREPLY=($(compgen -f -- "$cur"))
            return
            ;;
        --duration|-d|--sample-rate|-r|--lufs|--peak|--seed)
            return
            ;;
    esac

    if [[ $cur == -* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
    fi
}

complete -F _noisetool_completion noisetool
"""


def install_completion(shell: str = "bash") -> str:
    """Return instructions for installing shell completion."""
    rc_files = {
        "bash": "~/.bashrc",
        "zsh": "~/.zshrc",
        "fish": "~/.config/fish/completions/noisetool.fish",
    }
    rc = rc_files.get(shell, "~/.bashrc")
    if shell == "fish":
        return f"Copy {SHELL_COMPLETION_SCRIPT} to {rc}"
    return f"Add the following to {rc}:\n\n{SHELL_COMPLETION_SCRIPT}"


def add_completion_args(parser: argparse.ArgumentParser) -> None:
    """Add completion-related arguments to an argparse parser."""
    parser.add_argument(
        "--generate-completion",
        type=str,
        default=None,
        metavar="SHELL",
        choices=["bash", "zsh", "fish"],
        help="Generate shell completion script for the specified shell",
    )
