# Validation Checklist

Run `python scripts/load_data.py` and confirm:

1. `protein.uniprot_accession` uniqueness holds (enforced by unique index).
2. Foreign key joins load non-empty records:
   - `protein_condensate`
   - `condensate_cmod`
   - `condensate_disease`
3. Query pages return expected rows for sample inputs:
   - Kinase: `F4JWP9`
   - Condensate: `E12AB6E0`
   - Disease: `DOID:9119`
4. Download endpoint returns CSV content.
5. Plot page creates `static/condensate_type_counts.png`.
