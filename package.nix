{ inputs, lib, ... }@args: self: super: rec {

  pyserver = super.python3Packages.buildPythonApplication rec {

    pname = "pyserver";
    version = "0.0.1";
    pyproject = true;

    src = fetchPypi {
      inherit pname version;
      hash  = "sha256-fba6fca9ee179e239ec34ef8cbd56331c46ad89e428c9db9c475c794f5fdb673";
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

    build-system = with python3Packages; [
      setuptools
    ];

    dependencies = with python3Packages; [
      colorlog
    ];

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
