PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS protein_condensate;
DROP TABLE IF EXISTS condensate_cmod;
DROP TABLE IF EXISTS condensate_disease;
DROP TABLE IF EXISTS cmod;
DROP TABLE IF EXISTS disease;
DROP TABLE IF EXISTS publication;
DROP TABLE IF EXISTS condensate;
DROP TABLE IF EXISTS protein;

CREATE TABLE protein (
    protein_id INTEGER PRIMARY KEY AUTOINCREMENT,
    uniprot_accession TEXT NOT NULL UNIQUE,
    gene_name TEXT,
    protein_name TEXT,
    species_name TEXT,
    biomolecular_condensate_count INTEGER,
    synthetic_condensate_count INTEGER
);

CREATE TABLE condensate (
    condensate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    condensate_uid TEXT NOT NULL UNIQUE,
    condensate_name TEXT NOT NULL,
    condensate_type TEXT,
    species_tax_id INTEGER,
    proteins_count INTEGER,
    has_dna INTEGER,
    has_rna INTEGER,
    has_cmods INTEGER,
    has_condensatopathy INTEGER,
    confidence_score INTEGER
);

CREATE TABLE publication (
    pmid TEXT PRIMARY KEY
);

CREATE TABLE disease (
    disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_name TEXT NOT NULL UNIQUE
);

CREATE TABLE cmod (
    cmod_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cmod_name TEXT NOT NULL UNIQUE,
    biomolecular_type TEXT,
    phenotypic_class TEXT
);

CREATE TABLE protein_condensate (
    protein_condensate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    protein_id INTEGER NOT NULL,
    condensate_id INTEGER NOT NULL,
    evidence_source TEXT DEFAULT 'protein2cdcode_v2.1.tsv',
    UNIQUE (protein_id, condensate_id),
    FOREIGN KEY (protein_id) REFERENCES protein(protein_id),
    FOREIGN KEY (condensate_id) REFERENCES condensate(condensate_id)
);

CREATE TABLE condensate_cmod (
    condensate_cmod_id INTEGER PRIMARY KEY AUTOINCREMENT,
    condensate_id INTEGER NOT NULL,
    cmod_id INTEGER NOT NULL,
    pmid TEXT,
    UNIQUE (condensate_id, cmod_id, pmid),
    FOREIGN KEY (condensate_id) REFERENCES condensate(condensate_id),
    FOREIGN KEY (cmod_id) REFERENCES cmod(cmod_id),
    FOREIGN KEY (pmid) REFERENCES publication(pmid)
);

CREATE TABLE condensate_disease (
    condensate_disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
    condensate_id INTEGER NOT NULL,
    disease_id INTEGER NOT NULL,
    dysregulation_type TEXT,
    condensate_markers TEXT,
    pmid TEXT,
    FOREIGN KEY (condensate_id) REFERENCES condensate(condensate_id),
    FOREIGN KEY (disease_id) REFERENCES disease(disease_id),
    FOREIGN KEY (pmid) REFERENCES publication(pmid)
);

CREATE INDEX idx_protein_accession ON protein(uniprot_accession);
CREATE INDEX idx_protein_gene ON protein(gene_name);
CREATE INDEX idx_protein_species ON protein(species_name);

CREATE INDEX idx_condensate_uid ON condensate(condensate_uid);
CREATE INDEX idx_condensate_name ON condensate(condensate_name);

CREATE INDEX idx_pc_protein_id ON protein_condensate(protein_id);
CREATE INDEX idx_pc_condensate_id ON protein_condensate(condensate_id);

CREATE INDEX idx_cc_condensate_id ON condensate_cmod(condensate_id);
CREATE INDEX idx_cc_cmod_id ON condensate_cmod(cmod_id);
CREATE INDEX idx_cc_pmid ON condensate_cmod(pmid);

CREATE INDEX idx_cd_condensate_id ON condensate_disease(condensate_id);
CREATE INDEX idx_cd_disease_id ON condensate_disease(disease_id);
CREATE INDEX idx_cd_pmid ON condensate_disease(pmid);
