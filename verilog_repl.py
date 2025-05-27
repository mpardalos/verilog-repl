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
    for name, (vec, reg_expr) in env.items():
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


class VerilogRepl(cmd.Cmd):
    prompt = "iverilog> "
    env: Env = dict()
    debug: bool = True

    def emptyline():
        # Default behaviour is to repeat last command. Do nothing instead
        pass

    def do_eval(self, arg):
        """Evaluate a verilog expression"""
        verilog = verilog_of_expr(self.env, arg)
        if self.debug:
            print("---")
            print(verilog)
            print("---")
        run_verilog(verilog)

    def do_e(self, arg):
        """Alias for 'eval'"""
        return self.do_eval(arg)

    def do_reg(self, arg):
        """Add a reg definition"""
        if m := fullmatch(r"^\[(.+?)]\s+(\w+)\s+=\s+(.*?);?", arg):
            self.env[m[2]] = (m[1], m[3])
            print(f"Added reg [{m[1]}] {m[2]} = {m[3]} to environment")
        else:
            print("*** Unknown syntax")

    def do_env(self, arg):
        """Print the environment"""
        for name, (vec, reg_expr) in self.env.items():
            print(f"reg [{vec}] {name} = {reg_expr};")
        if not self.env.items():
            print("[empty]")

    def do_set(self, arg):
        """
        Set a flag on the REPL

        Only "debug" is supported for now
        """
        if arg == "debug":
            self.debug = True
        else:
            print(f"*** Unknown option '{arg}'")

    def do_unset(self, arg):
        """
        Set a flag on the REPL

        Only "debug" is supported for now
        """
        if arg == "debug":
            self.debug = False
        else:
            print(f"*** Unknown option '{arg}'")

    def do_EOF(self, arg):
        """Exit"""
        return True

    def do_q(self, arg):
        """Exit"""
        return True

    def do_quit(self, arg):
        """Exit"""
        return True

    def do_exit(self, arg):
        """Exit"""
        return True

if __name__ == "__main__":
    VerilogRepl().cmdloop()
