{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python314;
      in
      {
        packages.default = python.pkgs.buildPythonApplication {
          pname = "vt-automator";
          version = "0.1.0";
          src = ./app;
          format = "pyproject";
          nativeBuildInputs = [ python.pkgs.hatchling ];
          propagatedBuildInputs = [
            python.pkgs.flask
            python.pkgs.gunicorn
          ];
        };

        devShells.default = pkgs.mkShell {
          devShells.default = import ./shell.nix { inherit pkgs; };
        };
      }
    )
    // {
      nixosModules.default = import ./module.nix;
      overlays.default = final: prev: {
        vt-automator = self.packages.${final.system}.default;
      };
    };
}
