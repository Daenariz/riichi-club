{
  inputs,
  config,
  lib,
  pkgs,
  ...
}:

let
  cfg = config.services.riichi_club;
  domain = config.networking.domain;
  fqdn = if (cfg.nginx.subdomain != "") then "${cfg.nginx.subdomain}.${domain}" else domain;

  python-with-packages = pkgs.python3.withPackages (
    p: with p; [
      flask
      flask-wtf
      flask-sqlalchemy
      flask-migrate
      flask-login
    ]
  );

  inherit (lib)
    concatStringsSep
    getExe
    mkDefault
    mkEnableOption
    mkIf
    mkOption
    mkPackageOption
    types
    ;
in
{
  options.services.riichi_club = {
    enable = mkEnableOption "Riichi Club service.";

    package = mkPackageOption pkgs "riichi-club" { };

    secretKey = mkOption {
      type = types.str;
      description = "Secret key for the application.";
    };

    stateDir = mkOption {
      type = types.path;
      default = "/var/lib/riichi_club";
      description = "The directory to store the application's data.";
    };

    port = mkOption {
      type = types.port;
      default = 5000;
      description = "The port to listen on.";
    };

    user = mkOption {
      type = types.str;
      description = "The user the Flask service will run as.";
      default = "flaskapp";
    };

    group = mkOption {
      type = types.str;
      description = "The group the Flask service will run as.";
      default = "flaskapp";
    };

    nginx = {
      enable = mkOption {
        type = types.bool;
        default = true;
        description = "Enable Nginx as a reverse proxy for the Flask application.";
      };
      subdomain = mkOption {
        type = types.str;
        default = "riichi-club";
        description = "Subdomain for the Nginx virtual host. Leave empty for root domain.";
      };
      ssl = mkOption {
        type = types.bool;
        default = true;
        description = "Enable SSL for the Nginx virtual host using ACME.";
      };
    };

    gunicorn.extraArgs = mkOption {
      type = types.listOf types.str;
      default = [ ];
      description = "Extra arguments for gunicorn.";
    };
  };

  config = mkIf cfg.enable {
    nixpkgs.overlays = [ inputs.riichi-club.overlays.default ];

    systemd.tmpfiles.rules = [
      "d ${cfg.stateDir} 0750 ${cfg.user} ${cfg.group} - -"
    ];

    networking.firewall.allowedTCPPorts = [
      80 # ACME challenge
      443
    ];

    systemd.services.riichi_club-db-migrate = {
      description = "Riichi Club Database Migration";
      before = [ "riichi_club.service" ];
      environment = {
        PYTHONPATH = "${python-with-packages}/${python-with-packages.sitePackages}";
        DATABASE_URI = "sqlite:///${cfg.stateDir}/app.db";
        FLASK_APP = "run.py";
        SECRET_KEY = cfg.secretKey;
      };
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${getExe python-with-packages} -m flask db upgrade";
        WorkingDirectory = "${cfg.package}";
        User = cfg.user;
        Group = cfg.group;
      };
    };

    systemd.services.riichi_club = {
      description = "Riichi Club";
      after = [
        "network.target"
        "riichi_club-db-migrate.service"
      ];
      requires = [ "riichi_club-db-migrate.service" ];
      wantedBy = [ "multi-user.target" ];
      environment = {
        PYTHONPATH = "${python-with-packages}/${python-with-packages.sitePackages}";
        DATABASE_URI = "sqlite:///${cfg.stateDir}/app.db";
        SECRET_KEY = cfg.secretKey;
      };
      serviceConfig = {
        ExecStart = ''
          ${getExe pkgs.python3Packages.gunicorn} \
            --bind=127.0.0.1:${toString cfg.port} \
            ${concatStringsSep " " cfg.gunicorn.extraArgs} \
            app:app
        '';
        WorkingDirectory = "${cfg.package}";
        Restart = "on-failure";
        User = cfg.user;
        Group = cfg.group;
      };
    };

    users.users."${cfg.user}" = {
      home = "/var/lib/${cfg.user}";
      isSystemUser = true;
      group = cfg.group;
    };
    users.groups."${cfg.group}" = { };

    services.nginx = mkIf cfg.nginx.enable {
      enable = mkDefault true;
      virtualHosts."${fqdn}" = {
        enableACME = cfg.nginx.ssl;
        forceSSL = cfg.nginx.ssl;
        locations."/".proxyPass = "http://127.0.0.1:${toString cfg.port}";
      };
    };

    security.acme = mkIf (cfg.nginx.enable && cfg.nginx.ssl) {
      acceptTerms = true;
      defaults.email = mkDefault "postmaster@${domain}";
      defaults.webroot = mkDefault "/var/lib/acme/acme-challenge";
      certs."${domain}".postRun = "systemctl reload nginx.service";
    };
  };
}
