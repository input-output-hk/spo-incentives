#!/usr/bin/env python3
"""Transform §4 of README.md: insert umbrella sections, renumber headings, update all anchors and refs."""

import re

INPUT = '/sessions/brave-sharp-ramanujan/mnt/stream-SPO/spo-incentives/report/README.md'

with open(INPUT, 'r') as f:
    lines = f.readlines()

# ── 1. Build anchor mapping (old → new) for all §4 headings ──

# GitHub anchor rule: lowercase, strip non-alphanumeric except spaces/hyphens/em-dashes,
# replace spaces with hyphens. Em-dash (—) becomes -- (double hyphen). Do NOT collapse multiple hyphens.
def github_anchor(heading_text):
    """Generate GitHub-style anchor from heading text."""
    s = heading_text.strip()
    s = s.lower()
    # Remove characters that are not alphanumeric, space, hyphen, or em-dash
    out = []
    for ch in s:
        if ch == '—':
            out.append('--')
        elif ch.isalnum() or ch in (' ', '-'):
            out.append(ch)
    s = ''.join(out)
    s = s.replace(' ', '-')
    return s

# Old heading texts → new heading texts mapping
# We map (old_heading_text) → (new_level, new_heading_text)
# This drives both heading replacement and anchor mapping.

heading_map = {
    # stays
    '4. Cardano Reward System V2.0 Proposal': (1, '4. Cardano Reward System V2.0 Proposal'),
    '4.1 Constitutional framework': (2, '4.1 Constitutional framework'),
    # NEW: 4.2 Microeconomics — inserted separately
    '4.2 Guarantee operator viability across the entire productive population': (3, '4.2.1 Guarantee operator viability across the entire productive population'),
    '4.2.1 Problem statement': (4, '4.2.1.1 Problem statement'),
    '4.2.2 Structural: enforce the production threshold': (4, '4.2.1.2 Structural: enforce the production threshold'),
    '4.2.3 Economic: every productive pool must be profitable': (4, '4.2.1.3 Economic: every productive pool must be profitable'),
    '4.3 Restore the notion of pledge among operators': (3, '4.2.2 Restore the notion of pledge among operators'),
    '4.3.1 Problem statement': (4, '4.2.2.1 Problem statement'),
    '4.3.2 Specification': (4, '4.2.2.2 Specification'),
    '4.4 Maintain and diversify a competitive delegator yield': (3, '4.2.3 Maintain and diversify a competitive delegator yield'),
    '4.4.1 Make the base yield competitive': (4, '4.2.3.1 Make the base yield competitive'),
    '4.4.2 Make the yield reward operators who play the game': (4, '4.2.3.2 Make the yield reward operators who play the game'),
    '4.4.3 Diversify the delegation offer': (4, '4.2.3.3 Diversify the delegation offer'),
    '4.5 Reduce the concentration effects that distort both populations': (3, '4.2.4 Reduce the concentration effects that distort both populations'),
    '4.5.1 Problem statement': (4, '4.2.4.1 Problem statement'),
    '4.5.2 Entity-level awareness in reward distribution': (4, '4.2.4.2 Entity-level awareness in reward distribution'),
    '4.5.3 Differentiated delegation incentives — titans versus micro-delegators': (4, '4.2.4.3 Differentiated delegation incentives — titans versus micro-delegators'),
    # NEW: 4.3 Macroeconomics — inserted separately
    '4.6 The staking pot must survive reserve depletion': (3, '4.3.1 The staking pot must survive reserve depletion'),
    '4.7 The fee-generating population must expand': (3, '4.3.2 The fee-generating population must expand'),
    '4.8 The mechanism must function across a range of ADA price scenarios': (3, '4.3.3 The mechanism must function across a range of ADA price scenarios'),
    '4.9 The mechanism must be governable': (3, '4.3.4 The mechanism must be governable'),
    '4.10 Evaluation framework': (2, '4.4 Evaluation framework'),
}

# Evidence base and other h4 headings that become h5
h4_to_h5 = [
    'Evidence base',  # appears under 4.2.1 and 4.5.1
    'The operator side — multi-pool entity concentration',
    'The delegator side — titan delegators versus the micro-delegation tail',
]

# Build old_anchor → new_anchor mapping
anchor_map = {}
for old_text, (new_level, new_text) in heading_map.items():
    old_anchor = github_anchor(old_text)
    new_anchor = github_anchor(new_text)
    if old_anchor != new_anchor:
        anchor_map[old_anchor] = new_anchor

# Handle the special case: "4.5.1 Problem statement" has anchor "451-problem-statement-1" in TOC
# (GitHub appends -1 for duplicate anchors). We need to map that too.
# The second "Problem statement" under 4.5.1 gets -1 suffix in GitHub.
# In the new structure, 4.2.1.1 and 4.2.4.1 are both "Problem statement" at h4 level.
# The first one (4.2.1.1) gets no suffix, the second (4.2.4.1) gets -1.
# Old: 421-problem-statement (first), 451-problem-statement-1 (second)
# New: 4211-problem-statement (first), 4241-problem-statement (second... but it's still the second, so -1)
# Actually wait - "4.2.1.1 Problem statement" and "4.2.4.1 Problem statement" - let me compute anchors.
# 4211-problem-statement and 4241-problem-statement - these are DIFFERENT anchors now (different numbers).
# So no -1 suffix needed. But the OLD "451-problem-statement-1" needs to map to "4241-problem-statement".
anchor_map['451-problem-statement-1'] = '4241-problem-statement'
# And old "431-problem-statement" maps to "4221-problem-statement" (already covered above, but verify)
# Actually let me check: "4.3.1 Problem statement" → "4.2.2.1 Problem statement"
# old anchor: 431-problem-statement, new anchor: 4221-problem-statement ✓ (already in map)

# Also the old 421-problem-statement → 4211-problem-statement is already in the map.

# Also handle the sub-section anchors that include section numbers in the anchor:
# §4.2.2 and §4.2.3 sub-references like (#422-structural...) and (#423-economic...)
# These are already in the heading_map, which generates anchor_map entries.

# For h4→h5 headings (Evidence base, etc.), the anchors don't change because the heading text
# doesn't include section numbers. But we DO need to change # level. Handle in the line transformation.

# Also need to map §-text references (e.g., "§4.2" → "§4.2.1", etc.)
# These are inline text, not anchors.
section_text_map = {
    '§4.2': '§4.2.1',
    '§4.3': '§4.2.2',
    '§4.4': '§4.2.3',
    '§4.5': '§4.2.4',
    '§4.6': '§4.3.1',
    '§4.7': '§4.3.2',
    '§4.8': '§4.3.3',
    '§4.9': '§4.3.4',
    '§4.10': '§4.4',
    '§4.2.1': '§4.2.1.1',
    '§4.2.2': '§4.2.1.2',
    '§4.2.3': '§4.2.1.3',
    '§4.3.1': '§4.2.2.1',
    '§4.3.2': '§4.2.2.2',
    '§4.4.1': '§4.2.3.1',
    '§4.4.2': '§4.2.3.2',
    '§4.4.3': '§4.2.3.3',
    '§4.5.1': '§4.2.4.1',
    '§4.5.2': '§4.2.4.2',
    '§4.5.3': '§4.2.4.3',
}

# ── 2. Transform headings ──

# We need to detect §4 headings and transform them.
# §4 starts at "# 4. Cardano Reward System V2.0 Proposal"
# We need to be careful to only transform §4 headings, not §1-§3.

in_section4 = False
new_lines = []
# Track where to insert umbrella sections
insert_micro_after_line = None  # insert after the 4.1 section's last line before 4.2 heading
insert_macro_after_line = None  # insert after 4.5's last line before 4.6 heading

# First pass: identify heading lines and their line indices
heading_lines = {}  # line_index → (level, heading_text)
for i, line in enumerate(lines):
    m = re.match(r'^(#{1,6})\s+(.+)$', line.rstrip())
    if m:
        level = len(m.group(1))
        text = m.group(2).strip()
        heading_lines[i] = (level, text)

# Find the line indices for the key headings
line_of_42 = None  # "## 4.2 Guarantee..."
line_of_46 = None  # "## 4.6 The staking pot..."

for i, (level, text) in heading_lines.items():
    if text == '4.2 Guarantee operator viability across the entire productive population':
        line_of_42 = i
    elif text == '4.6 The staking pot must survive reserve depletion':
        line_of_46 = i

# ── 3. Process lines ──
# Track whether we're inside section 4 (for h4→h5 Evidence base changes)
section4_start = None
for i, (level, text) in heading_lines.items():
    if text == '4. Cardano Reward System V2.0 Proposal':
        section4_start = i
        break

# Track h4 headings that should become h5 within §4
# These are "#### Evidence base", "#### The operator side...", "#### The delegator side..."
# They only exist within §4 and need to go from h4 to h5.

result_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Check if this is where we insert the microeconomics umbrella (before old §4.2)
    if i == line_of_42:
        # Insert new §4.2 umbrella heading + intro paragraph
        result_lines.append('\n')
        result_lines.append('## 4.2 Microeconomics — participant incentives and market structure\n')
        result_lines.append('\n')
        result_lines.append('The first group of milestones addresses the microeconomics of the mechanism: the participant-level incentive structures that shape operator behaviour, pledge commitment, delegator yield, and market concentration. These are the problems that manifest at the individual actor level — the reward curve, the fee structure, the pledge function, and the entity-recognition gap — and their resolution is a precondition for the macroeconomic sustainability addressed in [§4.3](#43-macroeconomics--a-self-sustaining-and-governable-mechanism).\n')
        result_lines.append('\n')

    # Check if this is where we insert the macroeconomics umbrella (before old §4.6)
    if i == line_of_46:
        result_lines.append('\n')
        result_lines.append('## 4.3 Macroeconomics — a self-sustaining and governable mechanism\n')
        result_lines.append('\n')
        result_lines.append('The second group of milestones addresses the macroeconomics of the mechanism: the system-level sustainability conditions that determine whether the reward pipeline can fund itself beyond reserve depletion, expand its fee base, withstand external price shocks, and be recalibrated through on-chain governance. These milestones depend on the microeconomic foundations established in [§4.2](#42-microeconomics--participant-incentives-and-market-structure): a self-sustaining mechanism presupposes viable operators, meaningful pledge, competitive delegation, and a deconcentrated market.\n')
        result_lines.append('\n')

    # Check if this is a heading line that needs transformation
    m = re.match(r'^(#{1,6})\s+(.+)$', line.rstrip())
    if m and section4_start is not None and i >= section4_start:
        level = len(m.group(1))
        text = m.group(2).strip()

        if text in heading_map:
            new_level, new_text = heading_map[text]
            result_lines.append('#' * new_level + ' ' + new_text + '\n')
            i += 1
            continue

        # Check for h4→h5 headings (Evidence base, operator side, delegator side)
        if level == 4 and text in h4_to_h5:
            result_lines.append('##### ' + text + '\n')
            i += 1
            continue

    result_lines.append(line)
    i += 1

# ── 4. Replace anchors and §-references throughout the entire document ──

# Now do anchor replacements: (#old-anchor) → (#new-anchor)
# Sort by length descending to avoid partial replacements
sorted_anchors = sorted(anchor_map.items(), key=lambda x: len(x[0]), reverse=True)

# Also build §-ref replacements, sorted by length descending
sorted_section_refs = sorted(section_text_map.items(), key=lambda x: len(x[0]), reverse=True)

final_lines = []
for line in result_lines:
    # Replace anchors: (#old) → (#new)
    for old_anchor, new_anchor in sorted_anchors:
        line = line.replace('(#' + old_anchor + ')', '(#' + new_anchor + ')')

    # Replace §-text references
    # Need to be careful: §4.2.1 must be replaced before §4.2, etc.
    # The sorting by length descending handles this.
    # But we must avoid double-replacement: e.g., §4.2 → §4.2.1, then §4.2.1 → §4.2.1.1
    # So we do all replacements in one pass using regex.

    # Build a combined pattern for § refs
    # We need word-boundary-like matching: §4.2 should not match inside §4.2.1
    # Strategy: match §X.Y.Z only when NOT followed by .\d
    for old_ref, new_ref in sorted_section_refs:
        # Escape the dot for regex
        pattern = re.escape(old_ref)
        # Only replace if not followed by .\d (to avoid partial match of longer refs)
        # Since we're going longest-first, we can just do straight replacement
        # But we need to avoid re-replacing already-replaced text.
        # Actually, since we go longest first, §4.5.3 is replaced before §4.5,
        # so §4.5 replacement won't touch the already-replaced §4.2.4.3.
        # The issue is: after replacing §4.3 → §4.2.2, a later pass might see §4.2.2
        # and try to replace it as old §4.2.2 → §4.2.1.2. We need to prevent this.
        pass

    final_lines.append(line)

# The naive approach above won't work due to cascading replacements.
# Let's do a single-pass replacement using regex alternation.

def replace_section_refs(text, ref_map):
    """Replace §X.Y references in a single pass to avoid cascading."""
    # Build regex pattern matching any of the old refs, longest first
    sorted_refs = sorted(ref_map.keys(), key=len, reverse=True)
    # Escape for regex and ensure we match complete section numbers
    # §4.10 should match, §4.1 should not match §4.10
    patterns = []
    for ref in sorted_refs:
        escaped = re.escape(ref)
        # Must not be followed by \.\d or \d (to avoid matching §4.1 inside §4.10)
        patterns.append(escaped + r'(?![.\d])')

    combined = '|'.join(patterns)
    if not combined:
        return text

    def replacer(m):
        matched = m.group(0)
        return ref_map[matched]

    return re.sub(combined, replacer, text)

def replace_anchors(text, anc_map):
    """Replace (#old-anchor) in a single pass."""
    sorted_ancs = sorted(anc_map.keys(), key=len, reverse=True)
    patterns = []
    for anc in sorted_ancs:
        # Match (#anchor) - need to escape
        patterns.append(r'\(#' + re.escape(anc) + r'\)')

    combined = '|'.join(patterns)
    if not combined:
        return text

    def replacer(m):
        matched = m.group(0)
        # Extract old anchor from (#old-anchor)
        old_anc = matched[2:-1]  # strip (# and )
        return '(#' + anc_map[old_anc] + ')'

    return re.sub(combined, replacer, text)

# Redo the replacements properly with single-pass
final_lines = []
for line in result_lines:
    line = replace_anchors(line, anchor_map)
    line = replace_section_refs(line, section_text_map)
    final_lines.append(line)

# ── 5. Rewrite the TOC for §4 ──

# Find the TOC lines for §4 (lines 83-104 in original, 0-indexed: 82-103)
# We need to find them in final_lines. They start with "- [4." and are indented TOC entries.
# Let's find the TOC block boundaries.

toc_start = None
toc_end = None
for idx, line in enumerate(final_lines):
    if '- [4. Cardano Reward System V2.0 Proposal]' in line:
        toc_start = idx
    if toc_start is not None and toc_end is None:
        # The TOC block for §4 ends when we hit a line that doesn't start with spaces/- for §4
        # or starts a new top-level TOC entry (like "- [Sub-reports]")
        if idx > toc_start:
            stripped = line.strip()
            if not stripped.startswith('- [4.') and not stripped.startswith('- [4 '):
                toc_end = idx
                break

# New TOC for §4
new_toc = """- [4. Cardano Reward System V2.0 Proposal](#4-cardano-reward-system-v20-proposal)
  - [4.1 Constitutional framework](#41-constitutional-framework)
  - [4.2 Microeconomics — participant incentives and market structure](#42-microeconomics--participant-incentives-and-market-structure)
    - [4.2.1 Guarantee operator viability across the entire productive population](#421-guarantee-operator-viability-across-the-entire-productive-population)
      - [4.2.1.1 Problem statement](#4211-problem-statement)
      - [4.2.1.2 Structural: enforce the production threshold](#4212-structural-enforce-the-production-threshold)
      - [4.2.1.3 Economic: every productive pool must be profitable](#4213-economic-every-productive-pool-must-be-profitable)
    - [4.2.2 Restore the notion of pledge among operators](#422-restore-the-notion-of-pledge-among-operators)
      - [4.2.2.1 Problem statement](#4221-problem-statement)
      - [4.2.2.2 Specification](#4222-specification)
    - [4.2.3 Maintain and diversify a competitive delegator yield](#423-maintain-and-diversify-a-competitive-delegator-yield)
      - [4.2.3.1 Make the base yield competitive](#4231-make-the-base-yield-competitive)
      - [4.2.3.2 Make the yield reward operators who play the game](#4232-make-the-yield-reward-operators-who-play-the-game)
      - [4.2.3.3 Diversify the delegation offer](#4233-diversify-the-delegation-offer)
    - [4.2.4 Reduce the concentration effects that distort both populations](#424-reduce-the-concentration-effects-that-distort-both-populations)
      - [4.2.4.1 Problem statement](#4241-problem-statement)
      - [4.2.4.2 Entity-level awareness in reward distribution](#4242-entity-level-awareness-in-reward-distribution)
      - [4.2.4.3 Differentiated delegation incentives — titans versus micro-delegators](#4243-differentiated-delegation-incentives--titans-versus-micro-delegators)
  - [4.3 Macroeconomics — a self-sustaining and governable mechanism](#43-macroeconomics--a-self-sustaining-and-governable-mechanism)
    - [4.3.1 The staking pot must survive reserve depletion](#431-the-staking-pot-must-survive-reserve-depletion)
    - [4.3.2 The fee-generating population must expand](#432-the-fee-generating-population-must-expand)
    - [4.3.3 The mechanism must function across a range of ADA price scenarios](#433-the-mechanism-must-function-across-a-range-of-ada-price-scenarios)
    - [4.3.4 The mechanism must be governable](#434-the-mechanism-must-be-governable)
  - [4.4 Evaluation framework](#44-evaluation-framework)
"""

new_toc_lines = [l + '\n' for l in new_toc.strip().split('\n')]

# Replace the old TOC
final_lines = final_lines[:toc_start] + new_toc_lines + final_lines[toc_end:]

# ── 6. Write output ──
with open(INPUT, 'w') as f:
    f.writelines(final_lines)

print(f"Done. Wrote {len(final_lines)} lines.")
print(f"TOC replaced at lines {toc_start+1}-{toc_start+len(new_toc_lines)} (1-indexed)")
print(f"Anchor mappings applied: {len(anchor_map)}")
print(f"Section-ref mappings applied: {len(section_text_map)}")
