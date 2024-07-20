{ inputs, lib, ... }@args: self: super: rec {

  pyserver = super.python3Packages.buildPythonApplication rec {

    pname = "pyserver";
    version = "0.0.1";

    # Pull source from a Git server. Optionally select a specific `ref` (e.g. branch),
    # or `rev` revision hash.
    src = super.fetchFromGitHub rec {
      inherit pname version;
      name = pname;
      rev = version;
      owner = "Red-Flake";
      repo = "pyserver";
      sha256 = "sha256-WlZShvLkxl+gxL+iu7IQRQMgx59kZUgR6d6OGStfxS0=";
    };

    # If no `checkPhase` is specified, `python setup.py test` is executed
    # by default as long as `doCheck` is true (the default).
    # I want to run my tests in a different way:
    checkPhase = ''
      python -m unittest $(find tests -name "*.py")
    '';

    installPhase = ''install -Dm755 pyserver.py $out/bin/pyserver'';
    preFixup = ''
      makeWrapperArgs+=(--prefix PATH : ${args.lib.makeBinPath [
        # Hard requirements
        super.python3Packages.colorlog
      ]})
    '';

    # Meta information for the package
    meta = with lib; {
      description = "A simple multithreaded HTTP server with fancy directory listing and logging";
      homepage = "https://github.com/Red-Flake/pyserver";
      license = licenses.mit;
      maintainers = with maintainers; [ Mag1cByt3s ];
      platforms = lib.platforms.all;
      mainProgram = "pyserver";
    };
  };
}
