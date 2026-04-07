#!/bin/bash

VERSION="1.2.0"
PACKAGE="music-player_${VERSION}_all.deb"

echo "🔨 Building Music Player ${VERSION}"

mkdir -p musicplayer_deb/DEBIAN
mkdir -p musicplayer_deb/usr/local/bin
mkdir -p musicplayer_deb/usr/local/share/musicplayer
mkdir -p musicplayer_deb/usr/share/applications

cp music_player.py musicplayer_deb/usr/local/share/musicplayer/

cat > musicplayer_deb/usr/local/bin/music-player << 'EOF'
#!/bin/bash
python3 /usr/local/share/musicplayer/music_player.py
EOF
chmod +x musicplayer_deb/usr/local/bin/music-player

cat > musicplayer_deb/usr/share/applications/music-player.desktop << EOF
[Desktop Entry]
Version=${VERSION}
Type=Application
Name=Music Player
Comment=Modern Music Player for Linux
Exec=/usr/local/bin/music-player
Icon=audio-x-generic
Terminal=false
Categories=Audio;Music;
EOF

cat > musicplayer_deb/DEBIAN/control << EOF
Package: music-player
Version: ${VERSION}
Section: sound
Priority: optional
Architecture: all
Depends: python3, python3-tk, python3-pygame, python3-mutagen
Maintainer: Ilya <ilya@localhost>
Description: Modern Music Player
 Stylish music player with dark theme and playlist support.
Homepage: https://github.com/YOUR_USERNAME/music-player
EOF

dpkg-deb --build musicplayer_deb
mv musicplayer_deb.deb ${PACKAGE}
rm -rf musicplayer_deb

echo "✅ Created: ${PACKAGE}"
