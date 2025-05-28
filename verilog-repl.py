#!/usr/bin/env python3

from subprocess import DEVNULL, PIPE, run
import cmd
import readline
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Dict, Literal, Tuple
from re import fullmatch
from pprint import pprint
import os


type VarName = str
type VectorDeclaration = str
type Expression = str

type Env = Dict[VarName, Tuple[VectorDeclaration, Expression]]


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
    $finish;
end
endmodule"""


def run_verilog_iverilog(verilog: str):
    with TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "V.v").write_text(verilog)
        verilog_file = Path(tmpdir) / "V.v"
        vvp_file = Path(tmpdir) / "V.vvp"
        run(["iverilog", "-o", vvp_file, verilog_file])
        # Capture the output and drop the last line. The $finish prints out some
        # garbage that we want to hide
        output = run(["vvp", vvp_file], text=True, stdout=PIPE).stdout
        print("\n".join(output.splitlines()[:-1]))


def run_verilog_verilator(verilog: str):
    with TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "V.v").write_text(verilog)
        os.environ['LANG'] = 'C' # Supress perl errors in verilator
        run(
            ["verilator", "--binary", "--exe", "V.v", "-o", "V.bin"],
            cwd=tmpdir,
            stdout=DEVNULL
        )
        # Capture the output and drop the last line. The $finish prints out some
        # garbage that we want to hide
        output = run(
            ["./obj_dir/V.bin", "+verilator+quiet"], cwd=tmpdir, text=True, stdout=PIPE
        ).stdout
        print("\n".join(output.splitlines()[:-1]))


class VerilogRepl(cmd.Cmd):
    prompt = "iverilog> "
    env: Env = dict()

    debug: bool = False
    simulator: Literal["verilator", "iverilog"] = "iverilog"

    def emptyline(self):
        # Default behaviour is to repeat last command. Do nothing instead
        return False

    def do_eval(self, arg):
        """
        Evaluate a verilog expression. Accepts

        Usage:
            e <expr>                  Evaluate expression in a self-determined context
            e [<msb>:<lsb>] <expr>    Evaluate expression in a [<msb>:<lsb>] context
            e [<width>] <expr>        Evaluate expression in a [<width - 1>:0] context
        """

        verilog = verilog_of_expr(self.env, arg)
        if m := fullmatch(r'^\[(\d+:\d+)\]\s*(.*)', arg):
            vec, expr = m.groups()
            verilog = verilog_of_expr(self.env | {'__eval': (vec, expr)}, '__eval')
        elif m := fullmatch(r'^\[(\d+)\]\s*(.*)', arg):
            width, expr = m.groups()
            vec = f'{int(width)-1}:0'
            verilog = verilog_of_expr(self.env | {'__eval': (vec, expr)}, '__eval')

        if self.debug:
            print("---")
            print(verilog)
            print("---")

        match self.simulator:
            case "verilator":
                run_verilog_verilator(verilog)
            case "iverilog":
                run_verilog_iverilog(verilog)

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

        Flags:

          debug|nodebug
            Print extra debugging information (includes full module to be simulated)

          iverilog|verilator
            Simulator to use

        """
        match arg:
            case "debug":
                self.debug = True
            case "nodebug":
                self.debug = True
            case "iverilog":
                self.simulator = "iverilog"
                self.prompt = "iverilog> "
            case "verilator":
                self.simulator = "verilator"
                self.prompt = "verilator> "
            case _:
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
    print()
