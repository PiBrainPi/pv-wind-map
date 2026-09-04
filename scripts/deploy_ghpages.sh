#!/bin/bash
# gh-pages Deploy pv-wind-map — Worktree-Methode (CNAME bleibt unangetastet)
set -e
# TODO: Pfad anpassen, falls Repo woanders liegt
cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map

# 1) Worktree anlegen (prüft Branch remote zuerst)
git fetch origin gh-pages
rm -rf /tmp/gh-pages-wt-pvwind
git worktree add /tmp/gh-pages-wt-pvwind gh-pages

# 2) Deploy-Dateien aktualisieren (CNAME/Root-Struktur bleibt, kein dist/-Pickup)
cp dist/index.html /tmp/gh-pages-wt-pvwind/
cp dist/index_singlefile.html /tmp/gh-pages-wt-pvwind/
rm -rf /tmp/gh-pages-wt-pvwind/assets
mkdir -p /tmp/gh-pages-wt-pvwind/assets
cp dist/assets/*.json /tmp/gh-pages-wt-pvwind/assets/

# 3) Diagnose: kein dist/ im Index
if git -C /tmp/gh-pages-wt-pvwind ls-files | grep -q "^dist/"; then
  echo "FEHLER: dist/ im gh-pages-Index — Abbruch"
  exit 1
fi

# 4) Commit + Push
git -C /tmp/gh-pages-wt-pvwind add -A
git -C /tmp/gh-pages-wt-pvwind commit -m "deploy: $(date +%Y-%m-%d) — pv-wind-map Release" || echo "nichts zu committen"
git -C /tmp/gh-pages-wt-pvwind push origin gh-pages

# 5) Aufräumen
git worktree remove /tmp/gh-pages-wt-pvwind
git worktree list
echo "DEPLOY OK"
