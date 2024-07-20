{ lib
, stdenv
, fetchFromGitHub
, python3
, buildPythonPackage
, python3Packages
}:

buildPythonPackage rec {
  pname = "pyserver";
  version = "0.0.1";

  src = fetchFromGitHub {
    owner = "Red-Flake";
    repo = "pyserver";
    rev = "2f7dfda9808074a7fdac149abe8d3242e7a3ca19";
    hash = "sha256-WlZShvLkxl+gxL+iu7IQRQMgx59kZUgR6d6OGStfxS0=";
  };

  propagatedBuildInputs = with python3Packages; [
    colorlog
  ];

  meta = with lib; {
    description = "A simple multithreaded HTTP server with fancy directory listing and logging";
    homepage = "https://github.com/Red-Flake/pyserver";
    license = licenses.mit;
    maintainers = with maintainers; [ Mag1cByt3s ];
    platforms = platforms.all;
  };
}
