{
  python3,
  ...
}:

python3.pkgs.buildPythonApplication rec {
  pname = "riichi-club";
  version = "0.1.0";
  pyproject = true;

  build-system = [ python3.pkgs.setuptools ];

  dependencies = with python3.pkgs; [
    flask
    flask-wtf
    flask-sqlalchemy
    flask-migrate
    flask-login
  ];

  src = ../.;

  installPhase = ''
    runHook preInstall

    mkdir -p $out
    cp -r $src/app $out/
    cp -r $src/migrations $out/
    cp $src/run.py $out/
    cp $src/config.py $out/

    runHook postInstall
  '';

  doCheck = false;
}
