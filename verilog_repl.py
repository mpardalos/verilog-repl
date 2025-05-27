#!/usr/bin/env python3

from subprocess import run
import cmd
import readline
from tempfile import NamedTemporaryFile
from pathlib import Path
from typing import Dict


def verilog_of_expr(expr: str):
    return f"""module V;
initial $display("Decimal: |%d|", {expr});
initial $display("Hex:     |%h|", {expr});
initial $display("Binary:  |%b|", {expr});
endmodule
"""


def run_verilog(verilog: str):
    VVP_FILE = Path("./.temp.vvp").absolute()
    VERILOG_FILE = Path("./.temp.v").absolute()
    try:
        VERILOG_FILE.write_text(verilog)
        run(["iverilog", "-o", VVP_FILE, VERILOG_FILE])
        run(["vvp", VVP_FILE])
    finally:
        run(["rm", "-f", VVP_FILE, VERILOG_FILE])


def repl():
    while True:
        try:
            line = input("iverilog> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        if line in ["q", "quit", "exit"]:
            break
        else:
            run_verilog(verilog_of_expr(line.strip()))

    print()


if __name__ == "__main__":
    repl()
