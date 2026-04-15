# Matsuzakaya Mirror Context Dump

Date: 2026-04-15
Workspace: /home/amil/beauty
Scope requested: Download https://reielegance.com/matsuzakaya/ and save reusable script in src/

## Deliverables

1. Script saved at /home/amil/beauty/src/download_matsuzakaya.sh
2. Mirror output saved under /home/amil/beauty/site-mirror/reielegance.com/
3. This detailed context dump at /home/amil/beauty/src/matsuzakaya_context_dump.md

## What was run

Initial command attempted:
- wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --domains reielegance.com --directory-prefix /home/amil/beauty/site-mirror --execute robots=on --wait=1 --random-wait --user-agent "Mozilla/5.0 (compatible; SiteMirror/1.0)" "https://reielegance.com/matsuzakaya/"

Observed issue in initial run:
- Recursive query-string trap from links like ?close causing filenames such as index.html?close?close?... and near-infinite crawl behavior.
- Evidence included repeated lines with destination name too long and repeated fetches of matsuzakaya/?close?... variants.

Mitigation applied:
- Created a reusable script with reject regex filters to block known trap query patterns.
- Cleaned output and re-ran with the script.
- Identified and terminated an orphaned wget process from the first attempt.
- Removed leftover malformed ?close files.

## Saved script details

Script path:
- /home/amil/beauty/src/download_matsuzakaya.sh

Script behavior:
- Uses strict shell mode: set -euo pipefail
- Mirrors only matsuzakaya subtree with --no-parent
- Uses polite crawl settings: --wait=1 and --random-wait
- Preserves robots policy via --execute robots=on
- Converts links for local browsing via --convert-links and --adjust-extension
- Downloads page dependencies via --page-requisites
- Applies query rejection filters:
  - .*\?close.*
  - .*\?.*close.*
  - .*\?.*popup.*
  - .*\?.*modal.*

## Runtime timeline summary

1. Started mirror with base wget options.
2. Detected crawler trap in query parameters.
3. Stopped runaway session.
4. Wrote script to src/download_matsuzakaya.sh.
5. Executed script.
6. Detected orphan process from earlier run still active.
7. Killed orphan process.
8. Removed malformed ?close artifacts.
9. Verified final clean output stats.

## Terminal sessions involved

- b3893c3a-1347-4aa7-bf79-82b720214b06: initial run (runaway query loop)
- 4da63dce-4b14-4258-a778-7f840f66f459: first safer script run
- 3dae2fec-beef-4c1b-96dd-64b3140ab13e: clean regeneration run after output reset

## Final output verification

After cleanup and process termination:
- CLOSE_FILES=0
- TOTAL_FILES=74
- TOTAL_DIRS=31
- TOTAL_SIZE=1.2M
- TARGET_FILES=1
- TARGET_SIZE=44K

Target directory file list:
- /home/amil/beauty/site-mirror/reielegance.com/matsuzakaya/index.html

## Why target has one file

- The requested URL is a single page endpoint.
- Required assets are referenced from other site paths and were mirrored into their original paths under:
  - /home/amil/beauty/site-mirror/reielegance.com/wp-content/...
  - /home/amil/beauty/site-mirror/reielegance.com/wp-includes/...
- Therefore the page folder itself contains the HTML entry file while dependencies live in shared directories.

## Known limitations

- wget does not execute client-side JavaScript. Any JS-rendered content may not be fully captured.
- Pages requiring authenticated sessions, anti-bot checks, or dynamic API calls may be partially mirrored.
- robots policy was respected by design.

## Re-run instructions

From workspace root:
- chmod +x /home/amil/beauty/src/download_matsuzakaya.sh
- /home/amil/beauty/src/download_matsuzakaya.sh

Optional clean re-run:
- rm -rf /home/amil/beauty/site-mirror
- /home/amil/beauty/src/download_matsuzakaya.sh

## Troubleshooting notes

If query-loop artifacts reappear:
1. Check for old mirror processes:
   - ps -ef | grep -E "wget --mirror|download_matsuzakaya.sh" | grep -v grep
2. Kill any orphan process:
   - pkill -f "wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --domains reielegance.com"
3. Remove malformed files:
   - find /home/amil/beauty/site-mirror/reielegance.com -type f -name "*?close*" -delete
4. Re-run script.

## Compliance/ethics note

This mirror was configured with robots enabled and basic crawl throttling to reduce load and respect crawl directives.
