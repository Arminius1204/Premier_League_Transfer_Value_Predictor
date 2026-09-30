# Understat Player-Level Architecture Plan

## Issue Identification
During Phase 4, we validated that the Understat league-level page (`/league/EPL/{year}`) does not contain the `playersData` JSON structure. It solely provides `teamsData` and `datesData`.

## Proposed Collector Architecture
To capture individual player xG/xA without relying on a central league page, the acquisition engine must traverse the hierarchy:
`League -> Season -> Team -> Team Player Statistics`

1.  **Stage 1:** Extract `teamsData` from the League page (Completed in Phase 5). This provides a dictionary of internal Team IDs and Titles (e.g., `83` for Arsenal).
2.  **Stage 2:** Construct the Team-level URLs. The format is: `https://understat.com/team/{Team_Title}/{Year}`.
3.  **Stage 3:** Fetch and parse. The Team-level page contains the `playersData` JSON structure embedded within `<script>` tags, identical in format to our original regex attempt.

## Implementation Guardrails
*   **Request Frequency:** Hitting 20 teams across 3 seasons requires 60 HTTP requests. To respect server loads and avoid IP blocks, the collector must enforce a strict `time.sleep(3)` delay between requests, turning this into a ~3-minute job.
*   **Season Coverage:** Will explicitly map `2021`, `2022`, and `2023` paths.
*   **Expected Fields:** We expect to recover `goals`, `xG`, `assists`, `xA`, `shots`, `key_passes`, and `time` (minutes played) for every player that appeared for the club.

This architecture ensures we can safely, legally, and reliably recover advanced analytics for the Unified Data Warehouse in the future phases.
