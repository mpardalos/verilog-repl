# Verilog-REPL

Evaluate Verilog expressions interactively

## How to run this

If you're using nix:

``` sh
nix run github:mpardalos/verilog_repl
```

Otherwise, download `verilog_repl.py` from here and run it. You will need `iverilog`
available in your `$PATH`:

``` sh
wget https://raw.githubusercontent.com/mpardalos/verilog_repl/refs/heads/master/verilog_repl.py
chmod +x verilog_repl.py
./verilog_repl.py
```

## Usage

You can get help with `help` or `?`

```
iverilog> ?

Documented commands (type help <topic>):
========================================
EOF  e  env  eval  exit  help  q  quit  reg  set  unset
```

Evaluate Verilog expressions with `e <expr>`:

```
iverilog> e 32'd5 + 2'b01
Decimal: |         6|
Hex:     |00000006|
Binary:  |00000000000000000000000000000110|
```

You can also create registers (with a constant value) with `reg`

```
iverilog> reg [7:0] x = 8'd42;
Added reg [7:0] x = 8'd42 to environment
iverilog> reg [5:0] y = 8'd21;
Added reg [5:0] y = 8'd21 to environment
iverilog> e x + y
Decimal: | 63|
Hex:     |3f|
Binary:  |00111111|
```
