# Data Lineage Tracking Strategy

To guarantee the reproducibility and traceability of the Premier League Transfer Intelligence project, a lightweight metadata system has been conceptually designed alongside the Unified Data Warehouse.

## Core Lineage Chain
Every feature present in the downstream ML matrix must be completely traceable via the following sequence:

1.  **Source Identity:** `source` (e.g., Transfermarkt, FPL, football-data).
2.  **Raw File Artifact:** `source_file` (e.g., `/data/raw/transfermarkt/transfermarkt_pl_2023_2024.html`).
3.  **Parser Execution:** `parser_version` (The specific logic used in `/ml/data_parsing/` and `/ml/warehouse/`).
4.  **Canonical Linkage:** `master_player_id` generated via `/data/entity_resolution/`.
5.  **Warehouse Materialization:** `processing_timestamp` (When `build_warehouse.py` executed the transformation).

## Implementation Mechanism
Currently, lineage is functionally implemented through explicit source tracking keys in the CSV outputs:
*   `source_player_id`, `source_club_id`, and `source_transfer_id` are permanently preserved alongside `master_player_id` in `transfers_normalized.csv`.
*   The raw ingestion `.meta.json` files contain the original HTTP response status, fetch time, and exact endpoint URL.

*Future Enhancement:* Before finalizing the feature matrix, a global metadata index (e.g., `lineage.json`) will be exported on every run, locking the md5 hashes of the raw input files against the generated feature columns.
