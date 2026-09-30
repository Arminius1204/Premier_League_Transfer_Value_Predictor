# Season Standardization

## Objective
To ensure consistency across the entire Premier League Transfer Intelligence project, we must use a unified, canonical format for all football seasons. Different data sources represent seasons differently (e.g., "2023", "2023-2024", "2324"). Our system will standardise these internally before joining.

## Canonical Format
For all internal processing, documentation, and database storage, the canonical season format is:
**`YYYY/YY`** (e.g., `2023/24`)

## Internal Data Structure
Within the codebase (Python and Database), every season must be represented by the following attributes:

- **`season_id`**: String identifier (e.g., `"2023_2024"`). Used for safe filenames and database primary keys.
- **`season_label`**: The canonical display string (e.g., `"2023/24"`).
- **`start_year`**: Integer representing the year the season begins (e.g., `2023`).
- **`end_year`**: Integer representing the year the season ends (e.g., `2024`).

## Example Mapping

| Canonical (Label) | ID (File/DB Safe) | Start | End  | Source Specific Representations |
|-------------------|-------------------|-------|------|---------------------------------|
| `2022/23`         | `2022_2023`       | 2022  | 2023 | Transfermarkt: `2022`, football-data: `2223`, FBref: `2022-2023` |
| `2023/24`         | `2023_2024`       | 2023  | 2024 | Transfermarkt: `2023`, football-data: `2324`, FBref: `2023-2024` |
| `2024/25`         | `2024_2025`       | 2024  | 2025 | Transfermarkt: `2024`, football-data: `2425`, FBref: `2024-2025` |

## Enforcement
The ingestion layer must translate our canonical definitions into the specific string format required by the target URL. Downloaded raw files must use `season_id` in their filename.
