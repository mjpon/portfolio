#!/usr/bin/env sh
# Rebuilds site/vendor/anime.js, a trimmed copy of anime.js that only holds what site/motion.js uses.
# The site serves its own copy because the security policy only runs scripts from this domain.
# Needs Node and npm. Run from anywhere:  sh tools/vendor_anime.sh
set -eu
VERSION=4.5.0
HERE=$(cd "$(dirname "$0")" && pwd)
OUT="$HERE/../site/vendor"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"
npm init -y >/dev/null
npm install --silent "animejs@$VERSION" esbuild@0.25.10
cat > entry.js <<'EOF'
export { animate, createTimeline, spring, utils } from 'animejs';
export { createDrawable, createMotionPath } from 'animejs/svg';
EOF
mkdir -p "$OUT"
npx esbuild entry.js --bundle --format=esm --minify --legal-comments=none \
  --banner:js="/*! anime.js v$VERSION | MIT License | (c) Julian Garnier | https://animejs.com
 * Trimmed build: animate, createTimeline, spring, utils, createDrawable, createMotionPath.
 * Rebuild with tools/vendor_anime.sh */" \
  --outfile="$OUT/anime.js"
cp node_modules/animejs/LICENSE.md "$OUT/anime-LICENSE.md"
echo "wrote $OUT/anime.js"
