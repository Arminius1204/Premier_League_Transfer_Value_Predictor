# Transfer Fee & Currency Normalization Strategy

## Status
*   **Transfer Definitions Segregated:** DISCLOSED, UNDISCLOSED, FREE, and LOAN statuses have been fully isolated. 
*   **Target Eligible Constraint:** Only transfers classified as `DISCLOSED` and which parsed into valid numeric values are flagged as `target_eligible = TRUE`.
*   **Zero-Imputation Prevented:** `UNDISCLOSED` fees explicitly bypass the numeric extractor and remain null (`""`), avoiding artificial depression of the dependent variable.

## Currency Normalization
*   **Currently Present Currencies:** Transfermarkt primarily reports in `EUR` (€) and occasionally `GBP` (£) based on user locale or domain settings. Our scraped data consistently identified `EUR`.
*   **Exchange Rate Policy:** No historical currency conversions have been applied yet. As per the strict mandate against fabricating data, the `fee_gbp` column has been instantiated but remains blank. 
*   **Next Steps for Currency:** Before entering model training, an exchange-rate table must be ingested (e.g., European Central Bank historical daily rates) to join on `transfer_date` and accurately populate `fee_gbp`. Until then, we preserve the `raw_fee_string` and `fee_currency` natively.
