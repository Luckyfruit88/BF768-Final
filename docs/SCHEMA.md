# Schema Notes

This implementation creates a project-specific relational integration over source datasets.

## Core Tables

- `protein`: UniProt accession, gene/protein/species fields, counts.
- `condensate`: condensate UID/name/type and metadata flags.
- `protein_condensate`: custom association table linking proteins to condensates.
- `cmod`: c-mod catalog.
- `condensate_cmod`: c-mod evidence links, optionally with PMID.
- `disease`: disease identifiers (e.g., DOID values).
- `condensate_disease`: disease evidence links to condensates, with dysregulation text.
- `publication`: PMID evidence anchor.

## Why This Is Not a Raw Source Mirror

- Source rows are normalized into relational entities.
- Multi-valued fields from CSV files are split and loaded into association tables.
- Project-specific joins power three query workflows and CSV/plot outputs.
