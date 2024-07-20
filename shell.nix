{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.colorlog
  ];

  shellHook = ''
    echo "Entering Nix shell for pyserver development..."
    export PYTHONPATH=${pkgs.python311Packages.colorlog}/lib/python3.11/site-packages
  '';
}
