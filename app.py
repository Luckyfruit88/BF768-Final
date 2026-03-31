import csv
import io
import sqlite3
from pathlib import Path

from flask import Flask, Response, render_template, request


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "proteinatlas.db"
PLOT_PATH = ROOT / "static" / "condensate_type_counts.png"

app = Flask(__name__)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_csv_response(rows, filename):
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows([dict(r) for r in rows])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def query_kinase(accession):
    sql = """
    SELECT
        p.uniprot_accession,
        p.gene_name,
        p.protein_name,
        c.condensate_uid,
        c.condensate_name,
        c.condensate_type,
        c.confidence_score
    FROM protein p
    JOIN protein_condensate pc ON pc.protein_id = p.protein_id
    JOIN condensate c ON c.condensate_id = pc.condensate_id
    WHERE p.uniprot_accession = ?
    ORDER BY c.confidence_score DESC, c.condensate_name ASC
    """
    with get_conn() as conn:
        return conn.execute(sql, (accession.strip(),)).fetchall()


def query_condensate(uid):
    sql = """
    SELECT
        c.condensate_uid,
        c.condensate_name,
        p.uniprot_accession,
        p.gene_name,
        p.protein_name,
        p.species_name
    FROM condensate c
    JOIN protein_condensate pc ON pc.condensate_id = c.condensate_id
    JOIN protein p ON p.protein_id = pc.protein_id
    WHERE c.condensate_uid = ?
    ORDER BY p.gene_name ASC, p.uniprot_accession ASC
    """
    with get_conn() as conn:
        return conn.execute(sql, (uid.strip(),)).fetchall()


def query_disease(disease_name):
    sql = """
    SELECT
        d.disease_name,
        c.condensate_uid,
        c.condensate_name,
        cd.dysregulation_type,
        cd.condensate_markers,
        cd.pmid
    FROM disease d
    JOIN condensate_disease cd ON cd.disease_id = d.disease_id
    JOIN condensate c ON c.condensate_id = cd.condensate_id
    WHERE d.disease_name = ?
    ORDER BY c.condensate_name ASC, cd.pmid ASC
    """
    with get_conn() as conn:
        return conn.execute(sql, (disease_name.strip(),)).fetchall()


def generate_plot():
    # Lazy import to keep app startup lightweight.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT condensate_type, COUNT(*) AS n
            FROM condensate
            GROUP BY condensate_type
            ORDER BY n DESC
            """
        ).fetchall()
    if not rows:
        return False

    labels = [r["condensate_type"] or "unknown" for r in rows]
    counts = [r["n"] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, counts, color="#2E8B57")
    ax.set_title("Condensate Type Distribution")
    ax.set_ylabel("Count")
    ax.set_xlabel("Condensate Type")
    fig.tight_layout()
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PLOT_PATH, dpi=140)
    plt.close(fig)
    return True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/query/kinase")
def kinase_view():
    accession = request.args.get("accession", "").strip()
    rows = query_kinase(accession) if accession else []
    return render_template(
        "results.html",
        title="Kinase -> Condensates",
        columns=list(rows[0].keys()) if rows else [],
        rows=rows,
        query_type="kinase",
        query_value=accession,
    )


@app.route("/query/condensate")
def condensate_view():
    uid = request.args.get("uid", "").strip()
    rows = query_condensate(uid) if uid else []
    return render_template(
        "results.html",
        title="Condensate -> Proteins",
        columns=list(rows[0].keys()) if rows else [],
        rows=rows,
        query_type="condensate",
        query_value=uid,
    )


@app.route("/query/disease")
def disease_view():
    disease = request.args.get("name", "").strip()
    rows = query_disease(disease) if disease else []
    return render_template(
        "results.html",
        title="Disease -> Condensates + Evidence",
        columns=list(rows[0].keys()) if rows else [],
        rows=rows,
        query_type="disease",
        query_value=disease,
    )


@app.route("/download")
def download():
    query_type = request.args.get("type", "")
    q = request.args.get("q", "").strip()
    if query_type == "kinase":
        rows = query_kinase(q)
        return rows_to_csv_response(rows, f"kinase_{q or 'query'}.csv")
    if query_type == "condensate":
        rows = query_condensate(q)
        return rows_to_csv_response(rows, f"condensate_{q or 'query'}.csv")
    if query_type == "disease":
        rows = query_disease(q)
        safe = q.replace(" ", "_")
        return rows_to_csv_response(rows, f"disease_{safe or 'query'}.csv")
    return Response("Invalid query type", status=400)


@app.route("/plot")
def plot_view():
    ok = generate_plot()
    return render_template("plot.html", plot_exists=ok)


if __name__ == "__main__":
    app.run(debug=True)
