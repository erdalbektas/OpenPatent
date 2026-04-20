# Windows Installer Hotfix Watch (72 Hours)

Use this runbook after publishing the Windows installer reliability hotfix release.

## Scope

- Release version: `v1.2.17` (or the patch version used for this hotfix)
- Window: first 72 hours after publish
- Goal: detect and triage no-launch regressions before they spread

## Owners

- Primary: release owner
- Secondary: desktop maintainer
- Escalation: repository admin on-call

## Signals to Collect

- GitHub issues tagged with Windows launch failures
- Direct support reports that include "click icon, nothing happens"
- Startup logs from `%USERPROFILE%\.local\share\OpenPatent\log`
- Windows Event Viewer app crash entries (when available)

## Failure Buckets

Classify each incident into one of these buckets:

- `sidecar_missing`: packaged sidecar not present on disk
- `sidecar_blocked`: access denied/quarantined by Defender or EDR
- `webview2_missing`: app UI fails because WebView2 runtime is missing/outdated
- `startup_crash`: Rust/Tauri startup error before UI render
- `config_plugin_issue`: config/plugin state prevents initialization
- `unknown`: insufficient data

## Triage Checklist (per incident)

1. Confirm installed app version and installer filename.
2. Request latest log file and check for sidecar spawn errors.
3. Confirm whether `openpatent-cli` exists in install directory.
4. Check for Defender/AV quarantine events.
5. Confirm WebView2 runtime status.
6. Assign bucket and severity:
   - `sev1`: widespread/no workaround
   - `sev2`: frequent but recoverable
   - `sev3`: isolated edge case

## Response SLA

- First response: within 2 hours during the 72-hour watch window
- Bucket assignment: within 6 hours
- Workaround or fix direction: within 12 hours for `sev1`/`sev2`

## Escalation Triggers

Trigger fast-follow patch (`v1.2.18`) if any condition is met:

- 3+ confirmed `sidecar_missing` incidents
- 5+ total no-launch incidents across any bucket
- any `sev1` incident without workaround for 12+ hours

## End-of-Window Report

At 72 hours, publish a short summary:

- total incident count
- count per bucket
- top root cause
- follow-up actions and owners
- whether fast-follow patch is required
