#!/bin/sh
set -eu

ROOT="${1:-.}"

find "$ROOT" -maxdepth 4 -not -path '*/.git/*' \( \
  -iname '.env' -o \
  -iname '.env.*' -o \
  -iname '*.pem' -o \
  -iname '*.key' -o \
  -iname '*.p12' -o \
  -iname '*.pfx' -o \
  -iname 'id_rsa*' -o \
  -iname 'id_ed25519*' -o \
  -iname '*secret*' -o \
  -iname '*token*' -o \
  -iname '*credential*' -o \
  -iname '*credentials*' -o \
  -iname '*password*' -o \
  -iname '*passwd*' -o \
  -iname '*cookie*' -o \
  -iname '*cookies*' \
\) -print | sort
