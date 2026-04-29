{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python313.withPackages (ps: with ps; [
      requests
      beautifulsoup4
      lxml
      feedparser
    ]))
  ];
  
  shellHook = ''
    echo "✅ Python enviourement is ready"
    echo "📦 Installed packages: requests, beautifulsoup4"
  '';
}
