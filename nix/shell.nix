{
  pkgs ? import <nixpkgs> { },
  ...
}:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages (
      p: with p; [
        flask
        flask-wtf
        flask-sqlalchemy
        flask-migrate
        flask-login
        flask-babel
        gunicorn
      ]
    ))
    pkgs.nixfmt-tree
    pkgs.black
  ];
  shellHook = ''
    find . -type d -name "__pycache__" -exec rm -rf {} +
    export FLASK_APP=run.py
  '';
}
