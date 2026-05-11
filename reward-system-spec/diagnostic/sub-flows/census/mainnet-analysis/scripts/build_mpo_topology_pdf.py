"""Build a shareable PDF report from the MPO infrastructure-topology analysis.

Output: outputs/MPO_infrastructure_topology.pdf

Uses IOG brand palette and the two figures already generated under figures/.
Tables are reconstructed from data/*.csv so the PDF stays in sync if the
pipeline is re-run.
"""
from __future__ import annotations
import csv
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUTPUTS / "MPO_infrastructure_topology.pdf"

# --- helpers to read latest pipeline outputs ---
def _load_csv(path: Path) -> list:
    return list(csv.DictReader(open(path))) if path.exists() else []


def _read_headline():
    """Total pool count, total stake, MPO vs single-pool split from the endpoints CSV."""
    rows = _load_csv(ROOT / "data" / "mpo_relay_endpoints_resolved.csv")
    pools, mpo_entities, spo_entities, stake = set(), set(), set(), 0.0
    pool_stake = {}
    for r in rows:
        pools.add(r["pool_id_bech32"])
        pool_stake[r["pool_id_bech32"]] = float(r["current_active_stake_ada"] or 0)
        if r["category"] == "single_pool":
            spo_entities.add(r["entity_id"])
        else:
            mpo_entities.add(r["entity_id"])
    return {
        "pools": len(pools),
        "mpo_entities": len(mpo_entities),
        "spo_entities": len(spo_entities),
        "stake_ada": sum(pool_stake.values()),
        "endpoint_rows": len(rows),
    }

# IOG brand
INFARED = colors.HexColor("#E52321")
DAWN = colors.HexColor("#EC641D")
BLACK = colors.HexColor("#000000")
INK = colors.HexColor("#1a1a1a")
GREY_BG = colors.HexColor("#F4F4F4")
GREY_LINE = colors.HexColor("#CCCCCC")
COBALT = colors.HexColor("#2C4FFA")

styles = getSampleStyleSheet()


def style(name: str, **kw) -> ParagraphStyle:
    base = styles["BodyText"]
    s = ParagraphStyle(name, parent=base)
    for k, v in kw.items():
        setattr(s, k, v)
    return s


TITLE = style(
    "Title", fontName="Helvetica-Bold", fontSize=22, leading=26,
    textColor=BLACK, spaceAfter=4,
)
SUBTITLE = style(
    "Subtitle", fontName="Helvetica", fontSize=11, leading=14,
    textColor=INK, spaceAfter=18,
)
H1 = style(
    "H1", fontName="Helvetica-Bold", fontSize=15, leading=19,
    textColor=INFARED, spaceBefore=14, spaceAfter=6,
)
H2 = style(
    "H2", fontName="Helvetica-Bold", fontSize=12, leading=15,
    textColor=BLACK, spaceBefore=10, spaceAfter=4,
)
BODY = style(
    "Body", fontName="Helvetica", fontSize=10, leading=14,
    textColor=INK, spaceAfter=6, alignment=4,  # justify
)
SMALL = style(
    "Small", fontName="Helvetica", fontSize=8.5, leading=11,
    textColor=INK,
)
CAPTION = style(
    "Caption", fontName="Helvetica-Oblique", fontSize=8.5, leading=11,
    textColor=INK, spaceAfter=14, alignment=1,  # center
)
META = style(
    "Meta", fontName="Helvetica", fontSize=9, leading=12, textColor=INK,
)
FOOTNOTE = style(
    "Footnote", fontName="Helvetica-Oblique", fontSize=8, leading=10,
    textColor=colors.HexColor("#555555"),
)


def csv_rows(path: Path) -> list:
    return list(csv.DictReader(open(path)))


def make_table(rows, col_widths, header_style="infared") -> Table:
    header_bg = INFARED if header_style == "infared" else BLACK
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (-1, 0), (-1, -1), "LEFT"),  # last col left-aligned
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, header_bg),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, header_bg),
    ]))
    return t


def fmt_pct(x: float) -> str:
    return f"{x:.1f}%"


def fmt_ada(x: float) -> str:
    return f"{x/1e9:.2f}B"


def build_provider_table() -> Table:
    rows = csv_rows(DATA / "mpo_topology_concentration_by_provider.csv")
    rows = [r for r in rows if float(r["stake_split_pct"]) >= 0.5]
    rows.sort(key=lambda r: -float(r["stake_split_pct"]))
    data = [["Provider", "Stake (B ADA)", "Share", "Entities"]]
    for r in rows:
        data.append([
            r["provider"],
            fmt_ada(float(r["stake_split_ada"])),
            fmt_pct(float(r["stake_split_pct"])),
            r["entities"],
        ])
    return make_table(data, [6.6 * cm, 3 * cm, 2.4 * cm, 2.2 * cm])


def build_tier_table() -> Table:
    rows = csv_rows(DATA / "mpo_topology_concentration_by_tier.csv")
    rows.sort(key=lambda r: -float(r["stake_split_pct"]))
    data = [["Tier", "Stake (B ADA)", "Share", "Entities"]]
    for r in rows:
        data.append([
            r["tier"],
            fmt_ada(float(r["stake_split_ada"])),
            fmt_pct(float(r["stake_split_pct"])),
            r["entities"],
        ])
    return make_table(data, [6.6 * cm, 3 * cm, 2.4 * cm, 2.2 * cm])


def build_region_table() -> Table:
    rows = csv_rows(DATA / "mpo_topology_concentration_by_region.csv")
    hsc = [r for r in rows if r["region"].startswith(("aws:", "gcp:", "azure:"))]
    hsc.sort(key=lambda r: -float(r["stake_split_pct"]))
    hsc = hsc[:18]
    data = [["Hyperscaler region", "Stake (B ADA)", "Share", "Entities"]]
    for r in hsc:
        data.append([
            r["region"],
            fmt_ada(float(r["stake_split_ada"])),
            fmt_pct(float(r["stake_split_pct"])),
            r["entities"],
        ])
    return make_table(data, [6.6 * cm, 3 * cm, 2.4 * cm, 2.2 * cm], header_style="black")


def build_sensitivity_table() -> Table:
    rows = _load_csv(DATA / "mpo_topology_sensitivity.csv")
    # show only tier + provider dimensions, top categories
    keep = [r for r in rows if r["dimension"] in ("tier", "provider")]
    data = [["Dimension", "Key", "Even-split", "Majority", "Any-exposure"]]
    for r in keep[:18]:
        data.append([
            r["dimension"], r["key"],
            f"{float(r['even_split_pct']):.1f}%",
            f"{float(r['majority_pct']):.1f}%",
            f"{float(r['any_exposure_pct']):.1f}%",
        ])
    return make_table(data, [2.4 * cm, 5.0 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm])


def build_profile_diff_table() -> Table:
    rows = _load_csv(DATA / "mpo_topology_entity_profile_diff.csv")
    rows = [r for r in rows if r["category"] != "single_pool"][:18]
    head_style = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=8, leading=10,
                                textColor=colors.white)
    cell_style = ParagraphStyle("c", fontName="Helvetica", fontSize=7.8, leading=9.5,
                                textColor=INK)
    bold_style = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=7.8, leading=9.5,
                                textColor=INK)
    data = [[
        Paragraph("Entity", head_style),
        Paragraph("Pools", head_style),
        Paragraph("Stake (M ADA)", head_style),
        Paragraph("Dominant provider", head_style),
        Paragraph("Dominant region", head_style),
        Paragraph("Diversity H<sub>prov</sub>", head_style),
        Paragraph("Provider mix (top)", head_style),
    ]]
    for r in rows:
        data.append([
            Paragraph(r["display_name"], bold_style),
            Paragraph(r["pools"], cell_style),
            Paragraph(f"{int(r['stake_ada'])/1e6:.0f}", cell_style),
            Paragraph(f"{r['dominant_provider']} ({r['dominant_provider_share']}%)", cell_style),
            Paragraph(f"{r['dominant_region']} ({r['dominant_region_share']}%)", cell_style),
            Paragraph(r["provider_diversity_H"], cell_style),
            Paragraph(r["provider_mix"], cell_style),
        ])
    t = Table(data, colWidths=[2.6 * cm, 0.9 * cm, 1.5 * cm, 2.7 * cm, 3.1 * cm, 1.2 * cm, 5.0 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INFARED),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, INFARED),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, INFARED),
    ]))
    return t


def build_country_table() -> Table:
    rows = csv_rows(DATA / "mpo_topology_concentration_by_country.csv")
    rows = [r for r in rows if r["country_iso2"]]
    rows.sort(key=lambda r: -float(r["stake_split_pct"]))
    rows = rows[:8]
    data = [["Country", "Stake (B ADA)", "Share", "Entities"]]
    for r in rows:
        data.append([
            r["country_iso2"],
            fmt_ada(float(r["stake_split_ada"])),
            fmt_pct(float(r["stake_split_pct"])),
            r["entities"],
        ])
    return make_table(data, [6.6 * cm, 3 * cm, 2.4 * cm, 2.2 * cm], header_style="black")


def build_physical_country_table() -> Table:
    rows = csv_rows(DATA / "mpo_topology_concentration_by_physical_country.csv")
    rows = [r for r in rows if r["physical_country"]]
    rows.sort(key=lambda r: -float(r["stake_split_pct"]))
    rows = rows[:12]
    data = [["Physical country", "Stake (B ADA)", "Share", "Entities"]]
    for r in rows:
        data.append([
            r["physical_country"],
            fmt_ada(float(r["stake_split_ada"])),
            fmt_pct(float(r["stake_split_pct"])),
            r["entities"],
        ])
    return make_table(data, [6.6 * cm, 3 * cm, 2.4 * cm, 2.2 * cm], header_style="black")


def build_tau_sensitivity_table() -> Table:
    rows = _load_csv(DATA / "mpo_topology_tau_sensitivity.csv")
    head = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8.2, leading=10,
                          textColor=colors.white)
    cell = ParagraphStyle("tc", fontName="Helvetica", fontSize=7.8, leading=9.5, textColor=INK)
    breach = ParagraphStyle("tb", fontName="Helvetica-Bold", fontSize=7.8, leading=9.5,
                            textColor=INFARED)
    margin = ParagraphStyle("tm", fontName="Helvetica", fontSize=7.8, leading=9.5,
                            textColor=colors.HexColor("#2b8a3e"))
    # transpose so rows are scenarios and columns are tau values
    if not rows:
        return Table([["no data"]])
    taus = [r["tau_pct"] for r in rows]
    sc_keys = [k for k in rows[0].keys() if k not in ("tau_pct", "adversarial_threshold_pct")]
    sc_titles = {
        "joint_hyperscaler_outage_(aws_+_gcp_+_azure)": "Joint hyperscaler outage",
        "aws_us-east-1_cascade": "AWS us-east-1 cascade",
        "ovh_sbg_fire": "OVH SBG-style fire",
        "gcp_global_iam": "GCP global IAM outage",
        "azure_we_outage": "Azure westeurope outage",
        "aws_full_outage": "Complete AWS outage",
        "aws_plus_gcp": "AWS + GCP correlated",
        "frankfurt_metro": "Frankfurt metro-area outage",
        "all_hyperscalers": "All hyperscalers joint",
        "single_region_worst": "GCP europe-west3 (worst region)",
        "ovh_full": "Complete OVH outage",
        "hetzner_full": "Complete Hetzner outage",
    }
    data = [[Paragraph("Scenario", head)] +
            [Paragraph(f"&tau;={t}%<br/><font size=6>(adv {100-int(t)}%)</font>", head)
             for t in taus]]
    for sk in sc_keys:
        sc_label = sc_titles.get(sk, sk.replace("_", " "))
        row_cells = [Paragraph(sc_label, cell)]
        for r in rows:
            v = r[sk]
            if v == "BREACH":
                row_cells.append(Paragraph("BREACH", breach))
            else:
                row_cells.append(Paragraph(v, margin))
        data.append(row_cells)
    t = Table(data, colWidths=[5.6 * cm] + [2.2 * cm] * len(taus), repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INFARED),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def build_mpo_vs_spo_table() -> Table:
    rows = _load_csv(DATA / "mpo_topology_mpo_vs_spo.csv")
    head = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=8.2, leading=10,
                          textColor=colors.white)
    cell = ParagraphStyle("c", fontName="Helvetica", fontSize=8, leading=10, textColor=INK)
    bold = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=INK)
    rows = [r for r in rows
            if float(r["mpo_pct_of_mpo_cohort"]) + float(r["spo_pct_of_spo_cohort"]) > 1.0][:12]
    data = [[
        Paragraph("Provider", head),
        Paragraph("MPO cohort", head),
        Paragraph("Single-pool cohort", head),
        Paragraph("Asymmetry", head),
    ]]
    for r in rows:
        mpo_pct = float(r["mpo_pct_of_mpo_cohort"])
        spo_pct = float(r["spo_pct_of_spo_cohort"])
        delta = mpo_pct - spo_pct
        arrow = "MPO-heavy" if delta > 5 else ("SPO-heavy" if delta < -5 else "balanced")
        data.append([
            Paragraph(r["provider"], bold),
            Paragraph(f"{mpo_pct:.1f}% &nbsp;&nbsp;({int(r['mpo_stake_ada'])/1e6:.0f}M ADA)", cell),
            Paragraph(f"{spo_pct:.1f}% &nbsp;&nbsp;({int(r['spo_stake_ada'])/1e6:.0f}M ADA)", cell),
            Paragraph(f"{delta:+.1f} pts &mdash; {arrow}", cell),
        ])
    t = Table(data, colWidths=[3.8 * cm, 4.4 * cm, 4.4 * cm, 4.4 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INFARED),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def build_hhi_table() -> Table:
    rows = _load_csv(DATA / "mpo_topology_concentration_index.csv")
    head = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=8.2, leading=10,
                          textColor=colors.white)
    cell = ParagraphStyle("c", fontName="Helvetica", fontSize=8, leading=10, textColor=INK)
    bold = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=INK)
    data = [[
        Paragraph("Dimension", head),
        Paragraph("Distinct labels", head),
        Paragraph("HHI", head),
        Paragraph("Effective &#8470; of domains", head),
        Paragraph("Top-1 share", head),
        Paragraph("Concentration grade", head),
    ]]
    for r in rows:
        data.append([
            Paragraph(r["dimension"], bold),
            Paragraph(r["n_distinct_labels"], cell),
            Paragraph(r["HHI"], cell),
            Paragraph(r["effective_n_domains"], cell),
            Paragraph(f"{r['top1_share_pct']}%", cell),
            Paragraph(r["concentration_grade"], cell),
        ])
    t = Table(data, colWidths=[3.2 * cm, 2.4 * cm, 1.8 * cm, 2.8 * cm, 2.0 * cm, 4.6 * cm],
              repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INFARED),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def build_scenarios_table() -> Table:
    rows = _load_csv(DATA / "mpo_topology_failure_scenarios.csv")
    head = ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=8.2, leading=10,
                          textColor=colors.white)
    cell = ParagraphStyle("sc", fontName="Helvetica", fontSize=8, leading=10, textColor=INK)
    bold = ParagraphStyle("sb", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=INK)
    breached = ParagraphStyle("sx", fontName="Helvetica-Bold", fontSize=8, leading=10,
                              textColor=INFARED)
    data = [[
        Paragraph("Scenario", head),
        Paragraph("Stake at risk", head),
        Paragraph("% of total", head),
        Paragraph("Gap to 26%", head),
        Paragraph("Pools", head),
        Paragraph("Top entities at risk", head),
    ]]
    for r in rows:
        gap = float(r["gap_to_26pct"])
        is_breach = gap < 0
        gap_style = breached if is_breach else cell
        data.append([
            Paragraph(r["title"], bold),
            Paragraph(f"{int(r['stake_at_risk_ada'])/1e9:.2f}B ADA", cell),
            Paragraph(f"{r['stake_at_risk_pct']}%", cell),
            Paragraph(f"{'BREACH ' if is_breach else ''}{gap:+.2f}", gap_style),
            Paragraph(r["n_pools"], cell),
            Paragraph(r["top_entities"], cell),
        ])
    t = Table(data, colWidths=[4.0 * cm, 2.0 * cm, 1.4 * cm, 1.8 * cm, 1.0 * cm, 6.8 * cm],
              repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INFARED),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, INFARED),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, INFARED),
    ]))
    return t


def cross_check_table() -> Table:
    # Per-cell paragraph styles so long strings line-break inside the column.
    cell = ParagraphStyle(
        "Cell", fontName="Helvetica", fontSize=8.3, leading=10.5,
        textColor=INK, alignment=0,
    )
    head = ParagraphStyle(
        "CellHead", fontName="Helvetica-Bold", fontSize=8.8, leading=11,
        textColor=colors.white,
    )
    bold = ParagraphStyle(
        "CellBold", fontName="Helvetica-Bold", fontSize=8.3, leading=10.5,
        textColor=INK,
    )
    P = lambda s: Paragraph(s, cell)
    B = lambda s: Paragraph(s, bold)

    rows = [
        [
            Paragraph("Entity", head),
            Paragraph("Curated profile says", head),
            Paragraph("Topology pass observes", head),
            Paragraph("Verdict", head),
        ],
        [B("Coinbase"), P("Hidden behind bison.run / herd.run"),
         P("51% AWS (Tokyo, Ireland, Frankfurt) + 46% GCP (europe-west3)"),
         P("Six hyperscaler regions, two providers: most resilient observed")],
        [B("Everstake"), P("Multi-cloud, geo-distributed bare-metal"),
         P("OVH 33% / WorldStream 33% / Leaseweb 33%"),
         P("Multi-provider bare-metal: confirmed")],
        [B("Cardano Foundation"), P("(not in curated profiles)"),
         P("100% Green.ch (Swiss bare-metal)"),
         P("Single-provider, Swiss-resident")],
        [B("Kiln"), P("Institutional, dedicated infrastructure"),
         P("95% OVH"),
         P("Single-provider, French")],
        [B("Blockdaemon"), P("Multi-cloud, SOC 2 / ISO 27001"),
         P("100% GCP on the registered relays"),
         P("Profile claims wider scope than relays expose")],
        [B("Emurgo"), P("(IOG sister entity)"),
         P("97% OVH"),
         P("Single-provider, French")],
        [B("Figment"), P("Institutional staking, 70+ PoS networks"),
         P("38 SRV records under <i>*.cardano.aeq5f.com</i>; none resolve in public DNS"),
         P("Genuine DNS dead-end (intentional opaque routing)")],
    ]
    # Total inner width: A4 (21cm) - 4cm margins = 17cm. Distribute as 3 / 4.5 / 4.5 / 5cm.
    t = Table(rows, colWidths=[3.0 * cm, 4.5 * cm, 4.5 * cm, 5.0 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INFARED),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, INFARED),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, INFARED),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    # top accent
    canvas.setFillColor(INFARED)
    canvas.rect(0, h - 8, w, 8, fill=1, stroke=0)
    # footer line
    canvas.setStrokeColor(GREY_LINE)
    canvas.setLineWidth(0.4)
    canvas.line(2 * cm, 1.4 * cm, w - 2 * cm, 1.4 * cm)
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, 1.0 * cm, "ARC / IOG — MPO Infrastructure Topology")
    canvas.drawRightString(
        w - 2 * cm, 1.0 * cm, f"Page {doc.page}",
    )
    canvas.restoreState()


def build_pdf() -> Path:
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="MPO Infrastructure Topology — Concentration Findings",
        author="ARC / IOG",
        subject="Cardano MPO infrastructure concentration analysis",
    )
    story = []

    # --- cover header ----------------------------------------------------
    head = _read_headline()
    story.append(Paragraph("Cardano Infrastructure Topology", TITLE))
    story.append(Paragraph("Concentration findings for linear-Leios EB voting", SUBTITLE))
    today = date.today().strftime("%Y/%m/%d")
    story.append(Paragraph(
        f"Snapshot date: {today}  ·  Source: Koios <i>pool_list</i> + curated MPO mapping  ·  "
        f"Scope: <b>{head['pools']:,}</b> active pools / <b>{head['stake_ada']/1e9:.2f}B ADA</b> "
        f"covering the full Cardano network "
        f"(<b>{head['mpo_entities']}</b> MPO entities + <b>{head['spo_entities']:,}</b> "
        f"single-pool operators)",
        META,
    ))
    story.append(Spacer(1, 14))

    # --- executive summary -----------------------------------------------
    story.append(Paragraph("Executive summary", H1))
    story.append(Paragraph(
        "This pass resolves every registered relay endpoint across the full Cardano pool "
        "population to its hosting provider, ASN, country, and cloud region. The motivation is "
        "the linear-Leios EB voting rule from CIP-0164: with a high certification threshold "
        "(illustrated at &tau;=75% in the CIP), the spec itself acknowledges that "
        "&ldquo;a 26% stake attacker can trivially attack Leios throughput.&rdquo; The relevant "
        "concentration question is therefore whether any single failure domain encompasses "
        "&ge;26% of total productive stake.",
        BODY,
    ))
    story.append(Paragraph(
        "<b>No single cloud region holds more than ~5% of total productive stake.</b> The largest "
        "regional concentration is <b>GCP europe-west3 (Frankfurt) at 4.67%</b>, dominated by "
        "Coinbase. AWS ap-northeast-1 (Tokyo) follows at 4.06%; ap-northeast-2 (Seoul), "
        "eu-north-1 (Stockholm), eu-west-1 (Ireland), and Azure westeurope (Amsterdam) all sit "
        "between 2.5 - 3.2%. A single-region outage cannot by itself threaten the 75% EB quorum.",
        BODY,
    ))
    story.append(Paragraph(
        "Provider-level shares are higher: <b>AWS 22.7%, OVH 11.9%, GCP 11.6%, Hetzner 6.0%, "
        "Contabo 4.7%, Azure 4.0%, DigitalOcean 2.4%</b> of total productive stake. "
        "<b>Complete AWS unavailability silences 22.84% of stake &mdash; sitting only 3.16 points "
        "below the 26% spec-grounded threshold.</b> A correlated AWS+GCP outage silences 35.48% "
        "and crosses the threshold by 9.48 points. The full joint-hyperscaler scenario "
        "(AWS+GCP+Azure) silences 41.75%. The failure-scenarios section below quantifies eleven "
        "concrete plausible events.",
        BODY,
    ))
    story.append(Paragraph(
        f"Coverage: <b>{head['pools']:,} active pools / {head['stake_ada']/1e9:.2f}B ADA</b> — "
        f"the entire active Cardano pool population, including both the 85 MPO entities (~16.4B "
        "ADA) and the long tail of single-pool operators (~5.3B ADA). All percentages in this "
        "report are computed against this full base. The 6.7% \"Unresolved\" share is pools "
        "whose registered relays no longer resolve (stale DNS or decommissioned endpoints).",
        BODY,
    ))

    # --- concentration index --------------------------------------------
    story.append(Paragraph("Concentration at a glance", H1))
    story.append(Paragraph(
        "Two single-number summaries are useful before diving in. "
        "The <b>Herfindahl-Hirschman Index</b> (HHI) is the sum of squared "
        "stake-share fractions, scaled to 0&ndash;10,000 &mdash; the antitrust "
        "convention reads HHI &lt; 1,500 as low concentration, 1,500&ndash;2,500 "
        "as moderate, &gt; 2,500 as high. The <b>effective number of domains</b> "
        "is exp(Shannon entropy) and reads as &ldquo;how many equally-sized "
        "domains would give the same diversity as what is actually observed&rdquo;.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_hhi_table())
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The provider, region, and physical-country dimensions all read as "
        "low-concentration in the antitrust sense &mdash; ~11 effective providers "
        "and ~38 effective regions. The <b>tier</b> dimension is the only "
        "high-concentration aggregate: just ~3.8 effective tiers, because over "
        "97% of stake is split between only three structural layers (hyperscaler, "
        "commodity-VPS, on-prem). This is the shared-fate posture in a single "
        "number.",
        BODY,
    ))

    # --- provider chart --------------------------------------------------
    story.append(Paragraph("Hyperscaler vs commodity vs residential", H1))
    story.append(Paragraph(
        "Cardano's full active pool population splits roughly 40% / 31% / 19% across "
        "hyperscaler / commodity-VPS / on-prem-or-unclassified, with a small residential tail. "
        "Adding the long tail of single-pool operators on top of the MPO base lowers the "
        "hyperscaler share (single-pool operators run far more on Hetzner, Contabo, OVH, or "
        "self-hosted hardware than on AWS / GCP / Azure) and grows the commodity-VPS slice. "
        "The 19% \"other / on-prem\" is dominated by small ASNs that don't map to a recognised "
        "commercial hoster — bare-metal in residential or business broadband, regional hosters, "
        "and operators behind generic colocation.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_tier_table())
    story.append(Spacer(1, 8))
    img_provider = FIG / "mpo_topology_provider_tier.png"
    if img_provider.exists():
        story.append(Image(str(img_provider), width=16.5 * cm, height=10 * cm))
        story.append(Paragraph(
            "Figure 1. Stake-weighted infrastructure provider concentration across the full "
            "Cardano pool population. AWS, OVH, GCP, Hetzner, and Contabo are the top five.",
            CAPTION,
        ))

    # --- provider table --------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("Single-provider exposure", H1))
    story.append(Paragraph(
        "A complete AWS outage would silence ~23% of total productive stake — sitting right at "
        "the 25% threshold for EB quorum. A coordinated AWS + GCP outage (~34%) would cross it "
        "comfortably. OVH at 12% is the largest single-provider exposure outside the "
        "hyperscalers — a France-wide OVH incident would matter, though OVH's stake is more "
        "geographically dispersed across Roubaix, Strasbourg, Beauharnois, and Frankfurt.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_provider_table())

    # --- hyperscaler region chart ----------------------------------------
    story.append(Spacer(1, 16))
    story.append(Paragraph("Hyperscaler region exposure — the Leios-specific cut", H1))
    story.append(Paragraph(
        "PTR records expose the AWS region directly; GCP and Azure regions are derived from the "
        "providers' published IP-range manifests (Google's <i>cloud.json</i> and Microsoft's "
        "<i>ServiceTags_Public</i> JSON). This gives per-region exposure for every hyperscaler "
        "endpoint. <b>No single cloud region holds more than 5% of total productive stake.</b> "
        "The largest is GCP europe-west3 (Frankfurt), dominated by Coinbase, at 4.67%.",
        BODY,
    ))
    story.append(Paragraph(
        "Three observations: (1) The top regional concentrations cluster around Frankfurt, "
        "Tokyo, Seoul, Stockholm, Ireland, and Amsterdam — each within a couple percentage "
        "points of the others, each dominated by one or two entities. A region-level outage is "
        "primarily a <i>single-entity</i> event, not a multi-tenant collapse. (2) Coinbase "
        "deliberately spans <b>six distinct hyperscaler regions across two providers</b> (AWS "
        "Tokyo / Ireland / Frankfurt; GCP Frankfurt and others) — its Leios-vote liveness is "
        "structurally the most resilient. (3) The fragile single-region operators are still "
        "the same names from the MPO-only cut: <b>Upbit</b> sits almost entirely in AWS Seoul "
        "(ap-northeast-2), <b>CHUCK BUX</b> mostly in AWS Stockholm (eu-north-1), and "
        "<b>eToro</b> entirely in Azure westeurope.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_region_table())
    story.append(Spacer(1, 8))
    img_hsc = FIG / "mpo_topology_hyperscaler_region.png"
    if img_hsc.exists():
        story.append(PageBreak())
        story.append(Image(str(img_hsc), width=16.5 * cm, height=10.5 * cm))
        story.append(Paragraph(
            "Figure 2. Hyperscaler region stake exposure with dominant entity per region. "
            "AWS in red, GCP in orange, Azure in blue. The dashed grey line marks the 26% "
            "spec-grounded threshold (CIP-0164) &mdash; all observed regions sit well below.",
            CAPTION,
        ))

    # --- country / geo ---------------------------------------------------
    story.append(Paragraph("Geographic country distribution (physical datacentre)", H1))
    story.append(Paragraph(
        "The country aggregate below uses physical-datacentre country, derived from the cloud "
        "region (e.g., <i>aws:eu-west-1</i> &rarr; IE, <i>gcp:europe-west3</i> &rarr; DE, "
        "<i>azure:westeurope</i> &rarr; NL) for hyperscaler endpoints and from MaxMind "
        "GeoLite2-City for commodity-VPS endpoints. <b>Germany is the largest single physical "
        "country</b> at 19.9% because Frankfurt is a major hyperscaler / OVH / Hetzner hub. The "
        "United States follows at 19.2%; France at 11.0% reflects OVH's home country.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_physical_country_table())

    # --- cross-checks ----------------------------------------------------
    story.append(Spacer(1, 18))
    story.append(Paragraph("Cross-checks against curated MPO profiles", H1))
    story.append(Paragraph(
        "The diagnostic repo carries hand-curated profiles for the largest MPO entities. Below, "
        "each profile's self-disclosed posture is set against what the topology pass actually "
        "observes on the public-relay surface.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(cross_check_table())
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Two cross-check gaps are worth flagging. Blockdaemon's curated profile states "
        "multi-cloud infrastructure, but its registered Cardano relays all PTR-resolve under "
        "<i>*.bc.googleusercontent.com</i> — either the broader infrastructure runs producers "
        "that are masked behind the GCP-facing relays, or the Cardano product line specifically "
        "runs on GCP. Figment, after a fresh Koios re-harvest, is confirmed to register 38 SRV "
        "records pointing at <i>*.cardano.aeq5f.com</i> hosts that resolve to nothing in public "
        "DNS — this is a deliberate opaque-routing posture, not a data-collection gap, and "
        "Figment's 923M ADA is therefore unattributable from public-relay data alone.",
        BODY,
    ))

    # --- sensitivity -----------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("Sensitivity to the stake-attribution rule", H1))
    story.append(Paragraph(
        "Every percentage in this report uses an <b>even-split</b> rule: a pool that registers "
        "relays at AWS and Hetzner contributes 50/50 to each, so category totals sum to ~100%. "
        "To verify the headline numbers are not artefacts of that rule, the same metrics are "
        "re-computed under two alternatives: <b>majority</b> (the entire pool's stake is "
        "assigned to the most frequent label among its relays) and <b>any-exposure</b> "
        "(the pool's stake is counted in <i>every</i> distinct label it touches, so totals "
        "exceed 100% — useful for \"how much stake is at risk if X goes down\").",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_sensitivity_table())
    story.append(Paragraph(
        "Headline numbers are robust: tier shares move by less than three points across rules; "
        "AWS provider share is stable around 22-23%; OVH grows from 12% (even-split) to 16% "
        "(any-exposure) because OVH-multi-relay pools also touch other providers. The "
        "any-exposure column is the appropriate read for the Leios <b>liveness</b> question: "
        "even though only 22.7% of stake \"belongs\" to AWS under even-split, 22.8% is "
        "<b>exposed</b> to an AWS outage under any-exposure — essentially identical, meaning "
        "few multi-relay pools mix AWS with non-AWS infrastructure as a real diversification.",
        BODY,
    ))

    # --- profile diff ---------------------------------------------------
    story.append(Paragraph("Per-entity provider profile (top 18 by stake)", H1))
    story.append(Paragraph(
        "For each MPO entity, the table shows its dominant provider and region, its provider "
        "diversity (Shannon entropy in nats — 0 = single provider, log(N) = perfectly even "
        "across N), and the top provider mix. High diversity values (Coinbase, NuFi, Everstake) "
        "indicate operators with deliberate multi-cloud or multi-provider postures; zero values "
        "(Upbit, eToro, Cardano Foundation, YUTA, Wave, Adalite) are single-provider operators.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_profile_diff_table())

    # --- failure scenarios -----------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("Joint-failure scenarios &mdash; spec-grounded threshold analysis", H1))
    story.append(Paragraph(
        "CIP-0164 defines an EB as certified when the stake-weighted sum of committee votes "
        "exceeds a high threshold &tau; (illustrated at 75% in the CIP). The CIP's own security "
        "analysis states verbatim: <i>&ldquo;a 26% stake attacker can trivially attack Leios "
        "throughput with a 75% certification threshold.&rdquo;</i> The operational reading: "
        "if any failure domain encompasses &ge;26% of total productive voting stake, EB "
        "certification can be stalled. The table below quantifies eleven concrete plausible "
        "failure scenarios, each evaluated under an &ldquo;any-exposure&rdquo; rule &mdash; a "
        "pool is counted as at risk if <i>any</i> of its registered relays sits in the scenario's "
        "footprint. Scenarios marked BREACH cross the 26% line.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_scenarios_table())
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Two scenarios breach the spec-grounded threshold: a joint hyperscaler outage "
        "(AWS+GCP+Azure, 41.75% at risk) and a correlated AWS+GCP event (35.48%). Complete "
        "AWS unavailability alone sits at 22.84% &mdash; <b>only 3.16 points below the 26% "
        "line</b>, so any concurrent failure in a second cloud or in OVH pushes Cardano into "
        "the contested zone. Single-region outages (GCP europe-west3 at 4.67%, Azure "
        "westeurope at 3.07%) and historical-precedent events (OVH SBG fire at 12.37%) all "
        "sit comfortably below.",
        BODY,
    ))

    # --- tau sensitivity --------------------------------------------------
    story.append(Spacer(1, 12))
    story.append(Paragraph("Threshold sensitivity &mdash; how the picture shifts if &tau; moves", H1))
    story.append(Paragraph(
        "CIP-0164 leaves &tau; as a governance-tunable parameter. The 75% illustrative value "
        "yields a 26% adversarial threshold (the spec's own &ldquo;26% stake attacker&rdquo; "
        "figure). A lower &tau; relaxes the adversarial threshold; a higher &tau; tightens "
        "it. The table below re-evaluates every scenario across &tau; &isin; "
        "{60%, 70%, 75%, 80%, 90%}. <b>BREACH</b> means the scenario silences at least "
        "(100&minus;&tau;)% of stake; green margins show the remaining safety distance.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_tau_sensitivity_table())
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Three takeaways from the sensitivity. At a conservative &tau;=60%, only a perfectly "
        "correlated joint-hyperscaler event breaches; the network has substantial liveness "
        "margin. At the CIP's illustrative &tau;=75%, complete AWS alone is 2.2 points "
        "from breach. At &tau;=80%, <b>complete AWS unavailability alone breaches</b> &mdash; "
        "Cardano becomes liveness-fragile to a single-cloud failure. At &tau;=90%, every "
        "provider-level outage breaches and even Hetzner alone (1.9 points over) crosses the "
        "line. The choice of &tau; therefore directly trades off Leios safety against "
        "single-provider liveness risk.",
        BODY,
    ))

    # --- implications ----------------------------------------------------
    story.append(Paragraph("Implications for linear-Leios EB voting", H1))
    story.append(Paragraph(
        "Three structural observations follow from the scenarios table.",
        BODY,
    ))
    story.append(Paragraph("Same-region outage (one hyperscaler region)", H2))
    story.append(Paragraph(
        "Worst case is GCP europe-west3 (Frankfurt) at 4.67% &mdash; well below 26%. Leios EB "
        "voting continues. The affected entity itself halts &mdash; Upbit if Seoul (aws:"
        "ap-northeast-2) falls, eToro if Azure westeurope falls &mdash; but the network does "
        "not. Region-level concentration is therefore a single-entity reputational risk, not a "
        "network-liveness risk.",
        BODY,
    ))
    story.append(Paragraph("Single-provider outage (all of AWS)", H2))
    story.append(Paragraph(
        "AWS alone strips 22.84% of total productive stake &mdash; the closest single failure "
        "to the 26% line. The 3-point margin is thin enough that any concurrent failure (an "
        "OVH SBG-style fire while AWS is down, or a partial GCP regional outage) tips the "
        "network into a stall regime. This is the operationally most fragile single-cloud "
        "exposure in the data.",
        BODY,
    ))
    story.append(Paragraph("Correlated hyperscaler outage (the actual threat model)", H2))
    story.append(Paragraph(
        "An AWS+GCP correlated event (e.g., shared DNS / IAM / certificate-authority "
        "upstreams) silences 35.48% of stake and breaches the 26% threshold by 9.48 points. "
        "A full hyperscaler joint event (AWS+GCP+Azure) silences 41.75% and breaches by 15.75 "
        "points. AWS us-east-1 cascades have historically degraded GCP and Azure operations "
        "through shared upstreams, so this is not a hypothetical &mdash; it is the dominant "
        "structural risk visible in the data.",
        BODY,
    ))
    story.append(Paragraph(
        "The relevant risk metric is therefore not regional concentration but the "
        "<b>shared-fate footprint</b>: roughly two-fifths of total productive stake runs on top "
        "of three public-cloud control planes whose historical failure modes are correlated "
        "through shared DNS, certificate, BGP, and IAM upstreams.",
        BODY,
    ))

    # --- MPO vs single-pool ----------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("MPO vs single-pool: the asymmetric cohort risk", H1))
    story.append(Paragraph(
        "The headline percentages mix institutional MPO stake (15.76B ADA across 85 entities) "
        "with the long tail of single-pool operators (5.39B ADA across 2,072 entities). The "
        "two cohorts cluster on radically different infrastructure. The MPO cohort is "
        "hyperscaler-heavy &mdash; AWS, GCP, OVH, Azure dominate. The single-pool cohort is "
        "commodity-VPS- and self-hosted-heavy &mdash; the &ldquo;Other / on-prem&rdquo; "
        "category alone holds 43.6% of single-pool stake, mostly small regional hosters and "
        "home-broadband bare-metal.",
        BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(build_mpo_vs_spo_table())
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The asymmetry has a sharp implication. <b>Within the MPO cohort alone, AWS holds "
        "28.3%</b> &mdash; already over the 26% threshold derived from CIP-0164's "
        "illustrative &tau;=75%. The fact that single-pool operators run on a different "
        "infrastructure stack drags the network-wide AWS share down to 22.7%, but only "
        "because long-tail SPOs sit on Hetzner, Contabo, and home hardware. Any future shift "
        "of single-pool operators into hyperscaler hosting would directly erode this buffer.",
        BODY,
    ))
    story.append(Paragraph(
        "Read the other way round: the long tail of single-pool operators is a structurally "
        "valuable <i>diversification</i> for Cardano's liveness posture, not a "
        "decentralisation cost. The smallest operators are precisely the ones not on AWS.",
        BODY,
    ))

    # --- recommendations -------------------------------------------------
    story.append(Paragraph("Design options for Leios + V2 incentives", H1))
    story.append(Paragraph(
        "Five options grounded in the data above, ranging from least to most invasive.",
        BODY,
    ))
    story.append(Paragraph("1. Choose &tau; with an explicit single-cloud safety target", H2))
    story.append(Paragraph(
        "The &tau;-sensitivity table reads as a direct trade-off. Setting &tau;=70% gives "
        "Cardano a 7.2-point margin against complete-AWS outage; &tau;=80% reduces it to a "
        "BREACH. The CIP's illustrative &tau;=75% leaves a 2.2-point margin &mdash; tight. "
        "Governance should pick &tau; explicitly in awareness of the AWS dependency, not as "
        "a free parameter.",
        BODY,
    ))
    story.append(Paragraph("2. Shared-fate-aware committee sortition", H2))
    story.append(Paragraph(
        "CIP-0164's persistent + non-persistent voter sortition is currently stake-weighted "
        "and infrastructure-blind. A version that down-weights candidate voters whose "
        "registered relays cluster on already-represented (provider, region) pairs would "
        "produce committees whose failure modes are <i>de-correlated</i> by construction. "
        "This is a sortition modification only &mdash; no protocol-level change to the "
        "incentive layer.",
        BODY,
    ))
    story.append(Paragraph("3. V2 reward modulation against hyperscaler concentration", H2))
    story.append(Paragraph(
        "If the V2 reward formula incorporates an infrastructure-diversity coefficient "
        "(stake-weighted bonus for pools whose registered relays span &ge;2 providers, or "
        "penalty for top-1-provider concentration above a threshold), the incentive to "
        "diversify becomes direct. The diversity Shannon-entropy H computed in the "
        "profile-diff table is the natural metric.",
        BODY,
    ))
    story.append(Paragraph("4. Transparency requirement on producer-node location", H2))
    story.append(Paragraph(
        "The 22.84% AWS exposure is computed from registered relays only. The actual "
        "producer location is hidden by every serious operator, so the true concentration "
        "could be higher or lower. A protocol-level requirement to declare the producer's "
        "ASN (in the pool registration certificate, hashed if privacy-sensitive) would let "
        "future analyses ground in producer reality rather than relay proxy. This is a "
        "minor on-chain schema addition.",
        BODY,
    ))
    story.append(Paragraph("5. Reverse-decentralisation incentive: protect the long tail", H2))
    story.append(Paragraph(
        "The single-pool cohort's 43.6% &ldquo;Other / on-prem&rdquo; share is the most "
        "valuable diversification Cardano has. The V2 design should explicitly recognise "
        "this and avoid changes that would push small operators into hyperscaler hosting "
        "(e.g., per-block compute requirements they can only afford on managed cloud). The "
        "current pledge-bonus-forgoing equilibrium in the MPO cohort is unrelated to this "
        "structural diversification &mdash; the two should be addressed independently.",
        BODY,
    ))

    # --- appendix: sources and methodology -------------------------------
    story.append(PageBreak())
    story.append(Paragraph("Appendix &mdash; Sources and methodology", H1))

    story.append(Paragraph("Executive summary", H2))
    story.append(Paragraph(
        "The analysis combines four classes of data: live public-API fetches performed at "
        "analysis time, the diagnostic repository's existing curated MPO census, well-established "
        "public IP-attribution conventions encoded into the classifier, and a small number of "
        "standard cloud-region geography facts. Every concrete number in the tables and figures "
        "traces back to either a live fetch (with the raw response cached on disk) or a file in "
        "the diagnostic repository. The pipeline is fully reproducible: re-running "
        "<i>fetch_koios_pool_list.py</i> followed by <i>build_mpo_topology_concentration.py</i> "
        "against the same Koios snapshot reconstructs the analysis end to end.",
        BODY,
    ))

    story.append(Paragraph("Live data fetches performed at analysis time", H2))
    story.append(Paragraph(
        "The active-pool population and its registered relay set come from the public Koios "
        "<i>/pool_list</i> endpoint &mdash; 6,133 pool records covering the full Cardano network, "
        "of which 2,915 are active. No authentication, no rate limit hit, response cached to "
        "<i>data/koios_pool_list.json</i>. This is the source of the headline 2,915 pools / "
        "21.13B ADA figures.",
        BODY,
    ))
    story.append(Paragraph(
        "Forward DNS resolution uses the sandbox's stdlib <i>socket.getaddrinfo</i>. Reverse DNS "
        "(PTR) uses <i>dig +short -x &lt;ip&gt; @1.1.1.1</i> against Cloudflare's public "
        "resolver. Both are cached so the pipeline is idempotent.",
        BODY,
    ))
    story.append(Paragraph(
        "IP-to-ASN, country, and BGP-prefix attribution comes from Team Cymru's free bulk WHOIS "
        "service (<i>whois.cymru.com:43</i>), an industry-standard reference whose data is "
        "derived from public BGP routing tables. Every unique IP is queried in batches; results "
        "cached to <i>data/cache/asn_cymru.json</i>.",
        BODY,
    ))
    story.append(Paragraph(
        "Cloud-region attribution for the three largest hyperscalers uses each vendor's own "
        "authoritative published IP-range manifest. GCP regions are read from "
        "<i>https://www.gstatic.com/ipranges/cloud.json</i> (941 prefixes, each tagged with a "
        "region scope such as <i>europe-west3</i>). Azure regions are read from Microsoft's "
        "<i>ServiceTags_Public_YYYYMMDD.json</i> published under <i>download.microsoft.com</i> "
        "(3,136 service-tag entries). AWS regions are extracted directly from the PTR record, "
        "which encodes the region by convention "
        "(<i>ec2-X-X-X-X.eu-west-1.compute.amazonaws.com</i>).",
        BODY,
    ))
    story.append(Paragraph(
        "Sub-country location for OVH, Hetzner, Contabo, Leaseweb, and WorldStream comes from "
        "the MaxMind GeoLite2-City database, downloaded from a public mirror. GeoLite2 has known "
        "patchy coverage on some cloud blocks; cases where it returns only a country are flagged "
        "as such in the data.",
        BODY,
    ))

    story.append(Paragraph("Data from the diagnostic repository", H2))
    story.append(Paragraph(
        "The 901-pool / 16.40B ADA / 76.7%-productive-stake / 85-MPO-entity figures (the framing "
        "the original analysis question cited) come from the existing "
        "<i>mpo_entity_pool_mapping_mainnet.csv</i> and the diagnostic README, both already "
        "present in the repository before this analysis. The topology pass reads them rather "
        "than recomputing them.",
        BODY,
    ))
    story.append(Paragraph(
        "The curated entity profiles &mdash; the &ldquo;curated profile says&rdquo; column in "
        "the cross-checks table &mdash; are verbatim quotes from <i>profiles/coinbase.md</i>, "
        "<i>profiles/everstake.md</i>, <i>profiles/kiln.md</i>, <i>profiles/blockdaemon.md</i>, "
        "and related files. These are documents written by the diagnostic team; the topology "
        "pass does not modify or interpret them, only sets the curated claim alongside what "
        "registered-relay data actually shows.",
        BODY,
    ))

    story.append(Paragraph("Curated reference tables encoded in the classifier", H2))
    story.append(Paragraph(
        "The provider classifier uses two static reference tables maintained in "
        "<i>build_mpo_topology_concentration.py</i>: an ASN-to-provider mapping "
        "(<i>AS16509 &rarr; AWS</i>, <i>AS24940 &rarr; Hetzner</i>, <i>AS16276 &rarr; OVH</i>, "
        "<i>AS51167 &rarr; Contabo</i>, <i>AS59642 &rarr; Cherry Servers</i>, and others) and a "
        "PTR-pattern table (<i>*.amazonaws.com &rarr; AWS</i>, <i>*.your-server.de &rarr; "
        "Hetzner</i>, <i>*.bc.googleusercontent.com &rarr; GCP</i>, <i>*.cloudapp.net &rarr; "
        "Azure</i>, and others). These mappings are public conventions documented by each "
        "provider's own networking documentation and stable across years. They have not been "
        "fetched from a live authoritative source in this pipeline. For the major providers "
        "(AWS, GCP, Azure, OVH, Hetzner, Contabo, DigitalOcean) the mappings are well "
        "established. For the long-tail small hosters, the AS-name keyword fallback "
        "(<i>as_name</i> from Team Cymru) provides a cross-check.",
        BODY,
    ))
    story.append(Paragraph(
        "Cloud-region geography (<i>eu-north-1 = Stockholm</i>, <i>ap-northeast-1 = Tokyo</i>, "
        "<i>europe-west3 = Frankfurt</i>, <i>eu-west-1 = Ireland</i>, and similar) is also "
        "encoded from public AWS / GCP / Azure documentation rather than fetched live.",
        BODY,
    ))

    story.append(Paragraph("Independent cross-validation", H2))
    story.append(Paragraph(
        "An independent measurement by Cexplorer.io (article: <i>Cardano infrastructure under "
        "scrutiny</i>) reports node-count shares of AWS 16%, Contabo 11%, DigitalOcean 10%, "
        "Google Cloud 7%, and self-hosted 6.4%. This pass reports stake-weighted shares of "
        "AWS 22.7%, OVH 11.9%, GCP 11.6%, Contabo 4.7%, DigitalOcean 2.4%. The differences "
        "between the two sources are <b>consistent and structurally explained</b>: AWS and GCP "
        "host institutional MPOs with concentrated stake, so their <i>stake</i> shares exceed "
        "their <i>node</i> shares; Contabo and DigitalOcean host many small single-pool "
        "operators with low individual stakes, so their <i>node</i> shares exceed their "
        "<i>stake</i> shares. This is exactly the asymmetric-cohort effect the MPO-vs-"
        "single-pool table makes explicit. Programmatic cross-validation against a public "
        "JSON-format topology tracker was not feasible from the Cowork sandbox (pooltool / "
        "adapools APIs are not currently allowlisted); this remains the highest-value "
        "follow-up.",
        BODY,
    ))

    story.append(Paragraph("Interactive map artefact", H2))
    story.append(Paragraph(
        "A companion interactive Leaflet map ships alongside this report at "
        "<i>outputs/mpo_topology_map.html</i>. It plots one pin per active pool with "
        "resolvable geography (2,429 of 2,915 pools), colour-coded by dominant provider and "
        "sized by log of active stake. Click any pin to see the entity, full provider mix, and "
        "registered relay regions. The provider filter on the side panel toggles individual "
        "provider categories on/off. The map opens directly in any modern browser.",
        BODY,
    ))

    story.append(Paragraph("Inferences drawn from the data", H2))
    story.append(Paragraph(
        "A small number of entity-level statements combine direct observation with publicly "
        "known background. The claim that Upbit sits almost exclusively in AWS Seoul derives "
        "from direct PTR observation (their relays resolve to <i>ap-northeast-2</i> endpoints) "
        "combined with public knowledge that Upbit is a South Korean exchange. The claim that "
        "Coinbase has the most resilient observed posture is computed: six distinct hyperscaler "
        "regions across two providers, with a corresponding Shannon-entropy diversity score of "
        "0.802 nats in the profile-diff table. The OVH geographic spread (Roubaix, Strasbourg, "
        "Beauharnois, Frankfurt, Montr&eacute;al) is from direct GeoLite2 city lookup.",
        BODY,
    ))

    story.append(Paragraph("Known limitations of the data", H2))
    story.append(Paragraph(
        "Three weaknesses warrant explicit acknowledgement before the numbers are used to "
        "inform a Leios-design decision.",
        BODY,
    ))
    story.append(Paragraph(
        "The 26%-of-stake threshold used throughout the failure-mode analysis is taken directly "
        "from CIP-0164's own security analysis: <i>&ldquo;a 26% stake attacker can trivially "
        "attack Leios throughput with a 75% certification threshold.&rdquo;</i> The CIP does not "
        "bind a numeric value for the certification threshold &tau; (it is left to governance); "
        "75% is the illustrative value in the CIP. If governance selects a lower &tau; (e.g., "
        "60%), the corresponding adversarial-stake threshold relaxes proportionally and the gap "
        "in the scenarios table widens. The committee-selection function (Persistent Voters via "
        "Fait Accompli sortition + Non-persistent Voters via Poisson-distributed local "
        "sortition) introduces additional sampling variance that is not modelled here; the "
        "stake-share threshold is therefore a necessary-but-not-sufficient condition for "
        "liveness, and the scenarios table reads as a hazard inventory rather than a quorum-"
        "failure probability computation.",
        BODY,
    ))
    story.append(Paragraph(
        "The analysis describes registered relays, not block-producing nodes. Serious operators "
        "routinely hide producers behind public-facing relays in different facilities. The "
        "concentration figures are a <b>lower bound</b> on real operator-side concentration. "
        "Quantifying producer location from public data is non-trivial and out of scope for "
        "this pass; the most realistic route would be block-propagation timing analysis "
        "combined with a Cardano-node peer-state crawl.",
        BODY,
    ))
    story.append(Paragraph(
        "Country aggregation uses the IP-registration country reported by Team Cymru, which for "
        "hyperscaler-hosted endpoints reflects the company's home country (Amazon / Google / "
        "Microsoft all US-registered) rather than the physical datacentre. Country-level "
        "figures are therefore noisy; region-level figures are the faithful read of physical "
        "location.",
        BODY,
    ))

    story.append(Paragraph("Reproducibility", H2))
    story.append(Paragraph(
        "Every artefact under <i>outputs/</i>, <i>figures/</i>, and <i>docs/</i> is regenerated "
        "by running, in sequence: <i>fetch_koios_pool_list.py</i>, "
        "<i>build_mpo_topology_concentration.py all</i>, <i>build_mpo_topology_sensitivity.py</i>, "
        "<i>build_mpo_topology_figure.py</i>, <i>build_mpo_topology_pdf.py</i>. The intermediate "
        "caches under <i>data/cache/</i> make the pipeline idempotent &mdash; re-running picks "
        "up only changed inputs. The full pipeline takes roughly five minutes against the "
        "public APIs used.",
        BODY,
    ))

    # --- references ------------------------------------------------------
    story.append(Paragraph("References", H2))
    refs = [
        "Specification: <b>CIP-0164 &mdash; Ouroboros Linear Leios</b> (cips.cardano.org/cip/CIP-0164)",
        "Scenario library: <i>data/mpo_topology_failure_scenarios.csv</i> (built by <i>scripts/build_mpo_topology_scenarios.py</i>)",
        "Tau-sensitivity: <i>data/mpo_topology_tau_sensitivity.csv</i>",
        "MPO vs single-pool split: <i>data/mpo_topology_mpo_vs_spo.csv</i>",
        "Concentration index (HHI / effective domains): <i>data/mpo_topology_concentration_index.csv</i>",
        "Interactive map (HTML, opens in any browser): <i>outputs/mpo_topology_map.html</i> (built by <i>scripts/build_mpo_topology_map.py</i>)",
        "Cexplorer independent comparison: <i>cexplorer.io/article/cardano-infrastructure-under-scrutiny</i>",
        "Extra-metrics script: <i>scripts/build_mpo_topology_extra_metrics.py</i>",
        "Physical-country table: <i>data/mpo_topology_concentration_by_physical_country.csv</i>",
        "Koios pool snapshot: <i>data/koios_pool_list.json</i> (built by <i>scripts/fetch_koios_pool_list.py</i>)",
        "MPO mapping: <i>data/mpo_entity_pool_mapping_mainnet.csv</i>",
        "Per-endpoint output: <i>data/mpo_relay_endpoints_resolved.csv</i>",
        "Concentration tables: <i>data/mpo_topology_concentration_by_{provider,tier,country,region}.csv</i>",
        "Entity &times; provider matrix: <i>data/mpo_topology_entity_provider_matrix.csv</i>",
        "Sensitivity analysis: <i>data/mpo_topology_sensitivity.csv</i>",
        "Entity profile diff: <i>data/mpo_topology_entity_profile_diff.csv</i>",
        "Findings narrative: <i>docs/mpo_topology_findings.md</i>",
        "Pipeline: <i>scripts/build_mpo_topology_concentration.py</i>",
        "Sensitivity / profile-diff script: <i>scripts/build_mpo_topology_sensitivity.py</i>",
        "Figure script: <i>scripts/build_mpo_topology_figure.py</i>",
        "PDF script: <i>scripts/build_mpo_topology_pdf.py</i>",
        "ASN data: Team Cymru bulk WHOIS (whois.cymru.com:43)",
        "GCP IP ranges: gstatic.com/ipranges/cloud.json",
        "Azure ServiceTags: download.microsoft.com (Microsoft public JSON)",
        "GeoLite2-City: MaxMind (free database via public mirror)",
    ]
    for r in refs:
        story.append(Paragraph(f"&bull;  {r}", FOOTNOTE))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return OUT_PDF


if __name__ == "__main__":
    p = build_pdf()
    print(f"wrote {p}")
