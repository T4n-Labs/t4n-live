#!/bin/sh
# mkxbpskey.sh: buat file key xbps (.plist) dari public key OpenSSH.
# Pakai: ./mkxbpskey.sh private.pem.pub ["T4n Labs"] [folder-output]
set -eu

pub=${1:?pakai: $0 <public-key.pub> [signed-by] [folder-output]}
by=${2:-T4n Labs}
out=${3:-keys}

command -v ssh-keygen >/dev/null || { echo "ssh-keygen tidak ditemukan" >&2; exit 1; }

# 1) fingerprint MD5 -> nama file. Buang awalan "MD5:"
fp=$(ssh-keygen -E md5 -lf "$pub" | awk '{print $2}' | sed 's/^MD5://')

# 2) ukuran key (4096)
bits=$(ssh-keygen -lf "$pub" | awk '{print $1}')

# 3) public key OpenSSH -> PEM (BEGIN PUBLIC KEY)
pem=$(ssh-keygen -e -m PKCS8 -f "$pub")

# 4) PEM -> base64, diindent supaya rapi di dalam <data>
tab=$(printf '\t')
data=$(printf '%s\n' "$pem" | base64 | sed "s/^/$tab/")

mkdir -p "$out"
cat > "$out/$fp.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>public-key</key>
	<data>
$data
	</data>
	<key>public-key-size</key>
	<integer>$bits</integer>
	<key>signature-by</key>
	<string>$by</string>
</dict>
</plist>
PLIST

echo "dibuat: $out/$fp.plist"