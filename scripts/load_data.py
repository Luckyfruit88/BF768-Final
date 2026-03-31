import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "proteinatlas.db"
SCHEMA_PATH = ROOT / "db" / "schema.sql"


def yes_no_to_int(value: str) -> int:
    return 1 if str(value).strip().lower() == "yes" else 0


def split_tokens(value: str, separators: str = "|,"):
    if not value:
        return []
    text = str(value).strip()
    if text.lower() == "null":
        return []
    tokens = [text]
    for sep in separators:
        expanded = []
        for t in tokens:
            expanded.extend(t.split(sep))
        tokens = expanded
    return [t.strip() for t in tokens if t.strip() and t.strip().lower() != "null"]


def init_db(conn: sqlite3.Connection):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def load_proteins(conn: sqlite3.Connection):
    path = ROOT / "proteins.csv"
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append(
                (
                    r.get("Uniprot ID", "").strip(),
                    r.get("Gene Name", "").strip(),
                    r.get("Name", "").strip(),
                    r.get("Species", "").strip(),
                    int(r.get("Biomolecular condensate count", 0) or 0),
                    int(r.get("Synthetic condensate count", 0) or 0),
                )
            )
    conn.executemany(
        """
        INSERT INTO protein (
            uniprot_accession, gene_name, protein_name, species_name,
            biomolecular_condensate_count, synthetic_condensate_count
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def load_condensates(conn: sqlite3.Connection):
    path = ROOT / "condensates.csv"
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append(
                (
                    r.get("UID", "").strip(),
                    r.get("Name", "").strip(),
                    r.get("Condensate Type", "").strip(),
                    int(r.get("Species Tax Id", 0) or 0),
                    int(r.get("Proteins", 0) or 0),
                    yes_no_to_int(r.get("DNA", "")),
                    yes_no_to_int(r.get("RNA", "")),
                    yes_no_to_int(r.get("C-mods", "")),
                    yes_no_to_int(r.get("Condensatopathy", "")),
                    int(r.get("Confidence Score", 0) or 0),
                )
            )
    conn.executemany(
        """
        INSERT INTO condensate (
            condensate_uid, condensate_name, condensate_type, species_tax_id,
            proteins_count, has_dna, has_rna, has_cmods, has_condensatopathy, confidence_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def load_publications(conn: sqlite3.Connection):
    pmids = set()
    cmods_path = ROOT / "c-mods.csv"
    with open(cmods_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for pmid in split_tokens(row.get("PMID", "")):
                pmids.add(pmid)

    diseases_path = ROOT / "condensatopathies.csv"
    with open(diseases_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for pmid in split_tokens(row.get("PMID", "")):
                pmids.add(pmid)

    conn.executemany("INSERT OR IGNORE INTO publication (pmid) VALUES (?)", [(p,) for p in sorted(pmids)])


def load_protein_condensate(conn: sqlite3.Connection):
    path = ROOT / "protein2cdcode_v2.1.tsv"
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter="\t")
        pairs = []
        for row in reader:
            acc = row.get("uniprotkb_ac", "").strip()
            uid = row.get("condensate_id", "").strip()
            if not acc or not uid:
                continue
            pairs.append((acc, uid))

    for acc, uid in pairs:
        conn.execute(
            """
            INSERT OR IGNORE INTO protein_condensate (protein_id, condensate_id)
            SELECT p.protein_id, c.condensate_id
            FROM protein p
            JOIN condensate c ON c.condensate_uid = ?
            WHERE p.uniprot_accession = ?
            """,
            (uid, acc),
        )


def load_cmods_and_links(conn: sqlite3.Connection):
    path = ROOT / "c-mods.csv"
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cmod_name = row.get("C-mod name", "").strip()
            biomol = row.get("Biomolecular Type", "").strip()
            phen = row.get("Phenotypic Class", "").strip()
            conn.execute(
                """
                INSERT OR IGNORE INTO cmod (cmod_name, biomolecular_type, phenotypic_class)
                VALUES (?, ?, ?)
                """,
                (cmod_name, biomol, phen),
            )
            pmids = split_tokens(row.get("PMID", ""))
            condensates = split_tokens(row.get("Condensates", ""), separators="|")
            for uid in condensates:
                if not pmids:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO condensate_cmod (condensate_id, cmod_id, pmid)
                        SELECT c.condensate_id, m.cmod_id, NULL
                        FROM condensate c JOIN cmod m ON m.cmod_name = ?
                        WHERE c.condensate_uid = ?
                        """,
                        (cmod_name, uid),
                    )
                else:
                    for pmid in pmids:
                        conn.execute(
                            """
                            INSERT OR IGNORE INTO condensate_cmod (condensate_id, cmod_id, pmid)
                            SELECT c.condensate_id, m.cmod_id, ?
                            FROM condensate c JOIN cmod m ON m.cmod_name = ?
                            WHERE c.condensate_uid = ?
                            """,
                            (pmid, cmod_name, uid),
                        )


def load_diseases_and_links(conn: sqlite3.Connection):
    path = ROOT / "condensatopathies.csv"
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            condensates = split_tokens(row.get("Affected Condensates", ""), separators="|,")
            diseases = split_tokens(row.get("Diseases", ""), separators="|,")
            pmids = split_tokens(row.get("PMID", ""), separators=",|")
            dys = row.get("Dysregulation Type", "").strip()
            markers = row.get("Condensate markers", "").strip()

            if not diseases:
                continue

            for disease_name in diseases:
                conn.execute("INSERT OR IGNORE INTO disease (disease_name) VALUES (?)", (disease_name,))
                for uid in condensates:
                    if not pmids:
                        conn.execute(
                            """
                            INSERT INTO condensate_disease (
                                condensate_id, disease_id, dysregulation_type, condensate_markers, pmid
                            )
                            SELECT c.condensate_id, d.disease_id, ?, ?, NULL
                            FROM condensate c JOIN disease d ON d.disease_name = ?
                            WHERE c.condensate_uid = ?
                            """,
                            (dys, markers, disease_name, uid),
                        )
                    else:
                        for pmid in pmids:
                            conn.execute(
                                """
                                INSERT INTO condensate_disease (
                                    condensate_id, disease_id, dysregulation_type, condensate_markers, pmid
                                )
                                SELECT c.condensate_id, d.disease_id, ?, ?, ?
                                FROM condensate c JOIN disease d ON d.disease_name = ?
                                WHERE c.condensate_uid = ?
                                """,
                                (dys, markers, pmid, disease_name, uid),
                            )


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    load_proteins(conn)
    load_condensates(conn)
    load_publications(conn)
    load_protein_condensate(conn)
    load_cmods_and_links(conn)
    load_diseases_and_links(conn)
    conn.commit()

    counts = {}
    for table in [
        "protein",
        "condensate",
        "protein_condensate",
        "cmod",
        "condensate_cmod",
        "disease",
        "condensate_disease",
        "publication",
    ]:
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()

    print("Database loaded:", DB_PATH)
    for k, v in counts.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
