# Status Quo and CIP Formula Set (Shelley Spec-Aligned)

Source of truth for baseline notation and equations:
**Engineering Design Specification for Delegation and Incentives in Cardano-Shelley (SL-D1)**.

## Shared notation (SL-D1 style)

- $k$: target number of pools
- $z_0 := \frac{1}{k}$: saturation size (relative)
- $\sigma$: relative pool stake (relative to **total** stake, per SL-D1)
- $s$: relative owner-pledged stake (relative to **total** stake)
- $\sigma' := \min(\sigma, z_0)$
- $s' := \min(s, z_0)$
- $a_0 \in [0,\infty)$: pledge influence parameter
- $R$: total available rewards for the epoch (in ADA), after treasury allocation
- $\bar p$: apparent performance factor used for actual rewards
- $\hat f$: actual pool reward
- $c$: pool fixed cost
- $m \in [0,1]$: pool margin
- $t$: relative stake of a pool member

## 1) Status Quo (baseline from SL-D1)

Epoch reward pot to pools (compact form):

$$
R = (1-\tau)\left(F + D + \min(\eta,1)\rho\,(T_{\infty}-T)\right)
$$

where $F$ = transaction fees, $D$ = non-refundable deposits.

Optimal pool reward:

$$
f(s,\sigma)
=
\frac{R}{1+a_0}
\left(
\sigma' + s'a_0\cdot\frac{\sigma' - s'\left(\frac{z_0-\sigma'}{z_0}\right)}{z_0}
\right)
$$

Actual pool reward (performance-adjusted):

$$
\hat f(s,\sigma,\bar p) := \bar p \cdot f(s,\sigma)
$$

Operator reward:

$$
r_{\text{operator}}(\hat f,c,m,s,\sigma)=
\begin{cases}
\hat f, & \hat f \le c \\
c + (\hat f-c)\left(m + (1-m)\frac{s}{\sigma}\right), & \hat f > c
\end{cases}
$$

Member reward:

$$
r_{\text{member}}(\hat f,c,m,t,\sigma)=
\begin{cases}
0, & \hat f \le c \\
(\hat f-c)(1-m)\frac{t}{\sigma}, & \hat f > c
\end{cases}
$$

Pledge enforcement rule (SL-D1):

$$
\text{if pledge not met in epoch } \Rightarrow \hat f = 0
$$

---

## 2) CIP-0023 (formula delta only)

Baseline $f,\hat f$ unchanged.  
Fee split changes through margin floor clamp:

$$
m_{\text{eff}} := \max(m, m_{\min})
$$

and replace $m$ by $m_{\text{eff}}$ in:

$$
r_{\text{operator}}(\hat f,c,m,s,\sigma), \quad
r_{\text{member}}(\hat f,c,m,t,\sigma)
$$

So:

$$
r_{\text{operator}}^{(23)} = r_{\text{operator}}(\hat f,c,m_{\text{eff}},s,\sigma),\qquad
r_{\text{member}}^{(23)} = r_{\text{member}}(\hat f,c,m_{\text{eff}},t,\sigma)
$$

---

## 3) CIP-0082 (formula delta only)

### Stage 1

$$
c := 170
$$

### Stage 2

$$
c := 0,\qquad m_{\text{eff}} := \max(m, 0.03)
$$

Equivalent CIP statement:

$$
\text{poolRateEff} = \max(\text{poolRate},\text{minPoolRate})
$$

Apply $c=0$ and $m=m_{\text{eff}}$ in the same operator/member formulas.

### Stage 3 and Stage 4

$$
k:=750 \Rightarrow z_0=\frac{1}{750},\qquad
k:=1000 \Rightarrow z_0=\frac{1}{1000}
$$

Then recompute $\sigma'=\min(\sigma,z_0)$ and $s'=\min(s,z_0)$ in baseline $f(s,\sigma)$.

---

## 4) CIP-0050 (formula delta only)

Introduce leverage parameter $L$ and cap eligible stake by pledge leverage:

$$
\sigma'_L := \min(\sigma, z_0, Ls)
$$

Replace $\sigma'$ by $\sigma'_L$ in the pool reward equation:

$$
f^{(50)}(s,\sigma)
=
\frac{R}{1+a_0}
\left(
\sigma'_L + s'a_0\cdot\frac{\sigma'_L - s'\left(\frac{z_0-\sigma'_L}{z_0}\right)}{z_0}
\right)
$$

Actual rewards and splitting formulas stay the same form:

$$
\hat f^{(50)}=\bar p\cdot f^{(50)},\quad
r_{\text{operator}}^{(50)}=r_{\text{operator}}(\hat f^{(50)},c,m,s,\sigma),\quad
r_{\text{member}}^{(50)}=r_{\text{member}}(\hat f^{(50)},c,m,t,\sigma)
$$

---

## 5) CIP-0037 (formula delta only)

Dynamic saturation is pledge-dependent. Let:

$$
z_{\text{dyn}}(s) := z_0 \cdot \phi(s)
$$

with a floor and cap (normalized form consistent with CIP examples):

$$
\phi(s)=\max\!\left(\epsilon,\min\!\left(1,\frac{s}{s_{\text{ref}}}\right)\right)
$$

Then:

$$
\sigma'_{37}:=\min(\sigma,z_{\text{dyn}}(s))
$$

and replace $\sigma'$ by $\sigma'_{37}$ in baseline $f(s,\sigma)$:

$$
f^{(37)}(s,\sigma)
=
\frac{R}{1+a_0}
\left(
\sigma'_{37} + s'a_0\cdot\frac{\sigma'_{37} - s'\left(\frac{z_0-\sigma'_{37}}{z_0}\right)}{z_0}
\right)
$$

Actual rewards and splitting formulas keep the same form with $\hat f^{(37)}=\bar p f^{(37)}$.

---

## Composition rule (for combined scenarios)

- Choose one stake-eligibility rule: baseline / CIP-0050 / CIP-0037.
- Choose one fee rule: baseline / CIP-0023 / CIP-0082.
- Apply both to the same canonical SL-D1 pipeline:

$$
R \rightarrow f \rightarrow \hat f \rightarrow (r_{\text{operator}}, r_{\text{member}})
$$
