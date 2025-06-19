#!/bin/bash
set -euo pipefail

SCRIPT_FILE="$(cd "$(dirname "$0")/../bin" && pwd)/media-control"
VERSION="${1:-}"
VERSION="${VERSION#v}"

if [[ ! -f "$SCRIPT_FILE" ]]; then
  echo "Perl script not found: $SCRIPT_FILE"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid semver version string"
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working directory or index is not clean"
  git status --short
  exit 1
fi

if ! grep -qE "^use constant VERSION => '.*';" "$SCRIPT_FILE"; then
  echo "VERSION constant line not found in $SCRIPT_FILE."
  exit 1
fi

echo "Updating version in $SCRIPT_FILE to $VERSION"
perl -pi -e "s/^use constant VERSION => '.*';/use constant VERSION => '$VERSION';/" "$SCRIPT_FILE"

if git diff --quiet "$SCRIPT_FILE"; then
  echo "VERSION line did not change. Is it already set to $VERSION?"
  exit 1
fi

git add "$SCRIPT_FILE"
git commit -m "Bump version to $VERSION"
git tag "v$VERSION"

git push origin master
git push origin "v$VERSION"

echo "Version $VERSION successfully committed, tagged and pushed"
