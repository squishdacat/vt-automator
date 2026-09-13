{
  config,
  lib,
  pkgs,
  ...
}:

with lib;

let
  cfg = config.services.vt-automator;
  pythonEnv = pkgs.python314.withPackages (ps: [
    cfg.package
    ps.gunicorn
  ]);
in
{
  options.services.vt-automator = {
    enable = mkEnableOption "vt-automator dashcam FTP app";

    package = mkOption {
      type = types.package;
      default = pkgs.vt-automator;
      description = "The vt-automator package to use.";
    };

    databasePath = mkOption {
      type = types.path;
      default = "/var/lib/vt-automator/dashcam.db";
      description = "Path to the SQLite database file.";
    };

    bindAddress = mkOption {
      type = types.str;
      default = "127.0.0.1";
      description = "The address vt-automator will bind to. (Default: 127.0.0.1)";
    };

    port = mkOption {
      type = types.port;
      default = 8000;
      description = "Port for the Flask app to listen on.";
    };

    user = mkOption {
      type = types.str;
      default = "vt-automator";
      description = "User account under which the service runs.";
    };

    workers = mkOption {
      type = types.int;
      default = 4;
      description = "Number of gunicorn worker processes.";
    };
  };

  config = mkIf cfg.enable {
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.user;
    };
    users.groups.${cfg.user} = { };

    systemd.tmpfiles.rules = [
      "d ${dirOf cfg.databasePath} 0750 ${cfg.user} ${cfg.user} -"
    ];
    systemd.services.vt-automator = {
      description = "vt-automator dashcam FTP app";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        VT_AUTOMATOR_DB_PATH = cfg.databasePath;
      };

      serviceConfig = {
        ExecStart = ''
          ${pythonEnv}/bin/gunicorn vt_automator.app:app \
            --bind ${toString cfg.bindAddress}:${toString cfg.port} \
            --workers ${toString cfg.workers}
        '';
        User = cfg.user;
        Group = cfg.user;
        Restart = "on-failure";
      };
    };
  };
}
