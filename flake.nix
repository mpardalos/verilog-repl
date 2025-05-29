{
  description = "A REPL for Verilog expressions";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        runtimeDeps = [
          pkgs.iverilog
          pkgs.verilator
        ];

        deps = runtimeDeps ++ [
          pkgs.python3
        ];

        verilog-repl = pkgs.stdenv.mkDerivation {
          name = "verilog-repl";
          src = ./.;
          nativeBuildInputs = [ pkgs.makeWrapper ];
          installPhase = ''
            mkdir -p $out/bin
            cp verilog-repl.py $out/bin/verilog-repl.py
            makeWrapper ${pkgs.python3}/bin/python3 $out/bin/verilog-repl \
              --add-flags "$out/bin/verilog-repl.py" \
              --prefix PATH : ${pkgs.lib.makeBinPath runtimeDeps }
          '';
        };
      in
      {
        devShells.default = pkgs.mkShell { packages = deps; };

        packages.default = verilog-repl;

        apps.default = {
          type = "app";
          program = "${verilog-repl}/bin/verilog-repl";
        };
      }
    );
}
