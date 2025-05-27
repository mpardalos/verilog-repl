{
  description = "A REPL for Verilog expressions";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        deps = [
          pkgs.iverilog
          pkgs.verilator
          pkgs.python3
        ];

        verilog-repl = pkgs.writeShellApplication {
          name = "verilog-repl";
          runtimeInputs = deps;
          text = ''
            exec python3 ${./verilog-repl.py} "$@"
          '';
        };
      in {
        devShells.default =
          pkgs.mkShell { packages = deps; };

        apps.default = {
          type = "app";
          program = "${verilog-repl}/bin/verilog-repl";
        };
      });
}
