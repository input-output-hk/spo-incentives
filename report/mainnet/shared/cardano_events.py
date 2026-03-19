"""
Canonical Cardano mainnet event timeline for figure annotations.
"""

CARDANO_EVENTS = [
    # Hard forks / protocol upgrades
    (290, "Alonzo",         "#A700FF"),  # Smart contracts
    (365, "Vasil",          "#A700FF"),  # Plutus v2
    (394, "Valentine",      "#A700FF"),  # SECP primitives
    (503, "Chang",          "#A700FF"),  # On-chain governance
    (538, "Plomin",         "#A700FF"),  # Full governance

    # DeFi / ecosystem milestones
    (310, "SundaeSwap\nlaunch",   "#16E9D8"),  # First major DEX
    (321, "DeFi summer",          "#16E9D8"),  # Peak TVL wave
    (347, "NFT peak",             "#FFBA36"),  # NFT market peak

    # Market events
    (375, "Bear market\ntrough",  "#78909C"),  # Crypto winter bottom ~Nov 2022
    (560, "Bitcoin ETF\napproval", "#78909C"),  # Jan 2024 BTC ETF → inflows

    # Governance
    (517, "Constitutional\nCommittee",  "#06FF89"),  # First CC elected
]

# Subset for figures with limited horizontal space
CARDANO_EVENTS_COMPACT = [
    (290, "Alonzo",    "#A700FF"),
    (365, "Vasil",     "#A700FF"),
    (503, "Chang",     "#A700FF"),
    (538, "Plomin",    "#A700FF"),
    (347, "NFT peak",  "#FFBA36"),
    (560, "BTC ETF",   "#78909C"),
]


def add_event_markers(ax, events=None, y_frac=0.95, fontsize=7.5, alpha=0.5, rotation=0, compact=False):
    """Add vertical event marker lines and labels to a matplotlib axes.

    Parameters:
        ax: matplotlib axes
        events: list of (epoch, label, color) tuples. Defaults to CARDANO_EVENTS.
        y_frac: vertical position of label as fraction of axes height (0-1)
        fontsize: label font size
        alpha: line transparency
        rotation: label rotation angle
        compact: if True, use CARDANO_EVENTS_COMPACT by default
    """
    if events is None:
        events = CARDANO_EVENTS_COMPACT if compact else CARDANO_EVENTS

    xlim = ax.get_xlim()
    for epoch, label, color in events:
        if epoch < xlim[0] or epoch > xlim[1]:
            continue
        ax.axvline(epoch, color=color, linewidth=0.8, alpha=alpha, linestyle=":", zorder=1)
        ax.text(
            epoch + 1.5, y_frac, label,
            transform=ax.get_xaxis_transform(),
            fontsize=fontsize, color=color,
            alpha=min(1.0, alpha + 0.3),
            va="top", ha="left",
            rotation=rotation,
            fontweight="bold",
        )
