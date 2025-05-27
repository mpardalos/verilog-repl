#!/usr/bin/env python3

from subprocess import run
import cmd
import readline
from tempfile import NamedTemporaryFile
from pathlib import Path
from typing import Dict
from re import fullmatch
from pprint import pprint


type VarName = str
type VectorDeclaration = str
type Expression = str

type Env = Dict[VarName, (VectorDeclaration, Expression)]


def verilog_of_expr(env: Env, expr: str):
    declarations = ""
    for (name, (vec, reg_expr)) in env.items():
        declarations += f"reg [{vec}] {name} = {reg_expr};\n"

    return f"""module V;

{declarations}
initial begin
    $display("Decimal: |%d|", {expr});
    $display("Hex:     |%h|", {expr});
    $display("Binary:  |%b|", {expr});
end
endmodule"""


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
    env: Env = dict()
    debug = True

    while True:
        try:
            line = input("iverilog> ").strip()
            if line in ["q", "quit", "exit"]:
                break
            elif line == 'env':
                pprint(env)
            elif m := fullmatch(r'^set\s+debug$', line):
                debug = True
            elif m := fullmatch(r'^unset\s+debug$', line):
                debug = False
            elif m := fullmatch(r'^reg\s+\[(.+?)]\s+(\w+)\s+=\s+(.*?);?', line):
                env[m[2]] = (m[1], m[3])
                print(f"Added reg [{m[1]}] {m[2]} = {m[3]} to environment")
            else:
                verilog = verilog_of_expr(env, line)
                if debug:
                    print('---')
                    print(verilog)
                    print('---')
                run_verilog(verilog)
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            continue
    print()


if __name__ == "__main__":
    repl()
