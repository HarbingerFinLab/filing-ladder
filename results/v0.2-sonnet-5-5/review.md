# Human review — v0.2, Claude Sonnet 5.5

**Status: open; reviewer notes drafted 2026-11-09 on Parts A and C, verdicts not yet entered.** Prepared 2026-11-09 from `judgments.jsonl` and `transcripts.jsonl.gz` in this
directory. This file annotates the published run. It changes no score: the numbers in
[`README.md`](README.md) are final under tag `results-v0.2`. A gold found wrong is filed as a
**Gold correction** issue with the document evidence (see
[CONTRIBUTING](../../.github/CONTRIBUTING.md) §1) and recorded in the next protocol version; a
judge found wrong is recorded here, in the verdict column, and summarised in the README when this
review closes.

**Who reviews.** The harness author. That is the interest the disclosure names, so every verdict
cites where in the filing the reviewer read the value, and every transcript is public for a second
reader to check.

## Scope, computed

PROTOCOL §4 owes a human review of the disagreement log and a 20% random sample. This sheet takes,
from the 1,026 records of the nine rows:

- **Part A — the four questions no row answered**: zero correct readings out of 27 (nine rows ×
  three runs). Either every reader failed the same way, the gold is wrong, or the question cannot
  be answered from the filing it was resolved to.
- **Part B — where the hosted graph trailed the anchor or the package**: a question rung 2 or 4c
  answered 3 of 3 and 7a did not. Empty this run.
- **Part B′ — where only the hosted graph scored**: 7a was 3 of 3 and every other row 0 of 3.
  One question, and it is the case §11 pre-registered: the answer was read from a filing other
  than the question's (below, and `form-scoring.json`).
- **Part C — mixed cells**, where the same row's three runs split: the judge's consistency, or
  the model's.
- **Appendix D — the 20% random sample** the protocol names, drawn with a fixed seed. The judge's
  own repeatability on this sample, a second pass over the same 205 records, is reported at the
  end of this file.

Selection rule, reproducible: `correct` count per question over all 27 records is 0 (Part A);
`correct` on 7a < 3 while max(`correct`) over rung 2 and 4c = 3 (Part B); `correct` on 7a = 3
while every other row = 0 (Part B′); 0 < `correct` < 3 within one row (Part C); 205 records drawn
by `random.sample` over the judgments in file order, seed 20261109 (Appendix D).

| | |
|---|---|
| Part A | vals-16, vals-25, vals-43, vals-46 |
| Part B | — |
| Part B′ | vals-17 |
| Part C | 12 cells, 36 records |
| Appendix D | 205 records, seed 20261109 |

## The cross-filing rule, applied before publication

§11 says of 7a on the hosted repository: *the corpus is every processed filing, not 26 … an answer
read from a filing other than the question's is a confident-wrong of the form and is scored as
such.* Every 7a tool result was scanned for an SEC accession number other than the question's
filing's. **Six of 114 records read another filing**, all on Airbnb's FY2024 10-K: vals-17 (three
runs) and vals-22 (three runs) each needed the FY2022 gross booking value, which that filing does
not carry — rung 2 said so and abstained, and every file-based row scored 0 of 3 — and the model
fetched it from the FY2023 or FY2022 10-K through `search-text`'s `fiscal_year` argument or a
corpus-wide `search-documents`. The judge, which sees answer and gold only, marked five of the six
correct. Those five are re-scored as confident-wrong of the form in the README's 7a row (T2: 70% by
the judge, **61% form-scored**); `judgments.jsonl` and `summary.json` are the judge's output,
unchanged. The record list, the accessions read and the rule's text are in `form-scoring.json`.
This is the first time the rule has had something to apply to, and it is also a finding about the
gold: both questions' notes say the three years are in the FY2024 10-K's key metrics, and the
filing carries two.

## Part A — the four questions no row answered

### vals-16 — T2 lookup

**Question.** Summarize the key terms of the Series D mandatory convertible preferred stock (size of offering, closing date, price, liquidation preference, dividend rights, conversion terms, voting rights, purpose) that KKR & Co. (NYSE:KKR) offered in March 2025.

**Gold** (vals-expert): - Offering: 51,750,000 shares ($2,587,500,000 aggregate liquidation preference) of Series D Mandatory Convertible Preferred Stock, with an over-allotment option of 6,750,000 shares ($337,500,000 aggregate liquidation preference) - Closing/Settlement Date: March 7, 2025 - Price: $50.00 per share - Liquidation Preference: $50.00 per share, plus accumulated and unpaid dividends - Dividend: 6.25% per annum on the $50.00 liquidation preference, payable quarterly (Mar. 1, Jun. 1, Sept. 1, Dec. 1 of each year; starting Jun. 1, 2025 until Mar. 1, 2028) - No dividends on KKR common stock so long as Series D mandatory convertible prefs remain outstanding - Mandatory Conversion: Each share will automatically convert into 0.3312-0.4140 shares of KKR common stock on the mandatory conversion date (expected Mar. 1, 2028), based on avg. VWAP per share of KKR common stock over 20 consecutive trading day 

**Notes on the gold.** PARTIAL: the March 2025 Series D terms are prospectus-level (424B, not in the corpus); the Q1 2025 10-Q equity note carries size, closing, liquidation preference, dividend and conversion terms. Voting rights and use of proceeds may be absent

| Row | run | abstained | contradiction | rubric points | answer (first 240 chars) |
|---|---|---|---|---|---|
| 4c | 1 |  | yes | 5/11 | On March 7, 2025, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, a $2.59 billion aggregate liquidation preference (about $2.54 billion net proceeds). The liquidation preference is $50.00 per share plus |
| 4c | 2 |  |  | 6/11 | 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock were issued on March 7, 2025, for a $2.59 billion aggregate liquidation preference and $2,543.4 million of net proceeds. The liquidation preference is $50.00 per shar |
| 4c | 3 | yes |  | 6/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. The aggregate liquidation preference is $2.59 billion, and net proceeds were about $2.54 billion after issuance costs. The liquidation pr |
| 7a | 1 | yes |  | 5/11 | The 10-Q gives these terms. On March 7, 2025, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, a $2.59 billion aggregate liquidation preference and about $2.54 billion of net proceeds. The liquidation pr |
| 7a | 2 |  |  | –/– |  |
| 7a | 3 |  |  | –/– |  |
| 5c+doc | 1 |  |  | 5/11 | The filing states: 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock issued March 7, 2025, for $2.59 billion aggregate liquidation preference and about $2.54 billion net proceeds. The liquidation preference is $50.00 |
| 5c+doc | 2 |  |  | 6/11 | In March 2025 KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. That is $2.59 billion of aggregate liquidation preference, with net proceeds of about $2.54 billion. |
| 5c+doc | 3 |  | yes | 5/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. That is USD 2.59 billion of aggregate liquidation preference, or about USD 2.54 billion net of issuance costs. The liquidation preference |
| 7b+doc | 1 |  |  | 5/11 | Per the 10-Q, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. The aggregate liquidation preference is $2.59 billion, and net proceeds were about $2.54 billion. The liquidation preferenc |
| 7b+doc | 2 |  |  | 6/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. That is $2.59 billion of aggregate liquidation preference, or $50.00 per share, with net proceeds of about $2.54 billion. Dividends are c |
| 7b+doc | 3 |  |  | 6/11 | In March 2025, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. That is $2.59 billion aggregate liquidation preference, with net proceeds of about $2.54 billion. The liquidation preferen |
| 7c+doc | 1 |  |  | 5/11 | Per the 10-Q, on March 7, 2025 KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock. That is about $2.59 billion aggregate liquidation preference, with net proceeds of about $2.54 billion. The liquidation pre |
| 7c+doc | 2 |  |  | 6/11 | In March 2025 KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, with a $2.59 billion aggregate liquidation preference and about $2.54 billion of net proceeds. The shares were issued on March 7, 2025. The  |
| 7c+doc | 3 |  |  | 6/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. The aggregate liquidation preference is about $2.59 billion, and net proceeds were about $2.54 billion. The liquidation preference is $50 |
| 5c | 1 |  |  | 5/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, a $2.59 billion aggregate liquidation preference (USD). The liquidation preference is $50.00 per share plus accumulated and unpaid divide |
| 5c | 2 |  | yes | 5/11 | In March 2025 KKR & Co. Inc. issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, for a $2.59 billion aggregate liquidation preference. |
| 5c | 3 |  |  | 0/0 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, an aggregate liquidation preference of $2.59 billion. Net proceeds were about $2,543.4 million for the quarter ended March 31, 2025. The  |
| 7b | 1 |  |  | 5/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, for about $2.59 billion aggregate liquidation preference (net proceeds $2,543.4 million). The liquidation preference is $50.00 per share  |
| 7b | 2 |  |  | –/– |  |
| 7b | 3 |  |  | 5/11 | Per the filing, on March 7, 2025 KKR & Co. Inc. issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, a $2.59 billion aggregate liquidation preference. Each share has a $50.00 liquidation preference plus accumula |
| 7c | 1 |  |  | 5/11 | On March 7, 2025, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, a $2.59 billion aggregate liquidation preference. The liquidation preference is $50.00 per share plus accumulated and unpaid dividends.  |
| 7c | 2 |  |  | 6/11 | In March 2025 KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. That is $2.59 billion aggregate liquidation preference, with cash proceeds of about $2.54 billion. The liquidation preferen |
| 7c | 3 |  |  | 5/11 | In March 2025 (issued March 7, 2025), KKR issued 51.75 million shares of 6.25% Series D Mandatory Convertible Preferred Stock. The aggregate liquidation preference is about USD 2.59 billion, at USD 50.00 per share plus accumulated and unpai |
| 2 | 1 |  | yes | 5/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, with $2.59 billion aggregate liquidation preference (about $2.54 billion net proceeds). The liquidation preference is $50.00 per share pl |
| 2 | 2 |  |  | 5/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, with an aggregate liquidation preference of $2.59 billion (USD, $50.00 per share) and net proceeds of about USD 2.54 billion. Dividends a |
| 2 | 3 |  |  | 6/11 | Per the 10-Q, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025. The aggregate liquidation preference is $2.59 billion, or $50.00 per share, and net proceeds were about $2.54 billion (USD  |

**Reviewer note, drafted 2026-11-09, verdict open.** The 10-Q does not carry the gold. Its only
description of the Series D terms is the equity note ("Series D Mandatory Convertible Preferred
Stock", rung 2 text at about offset 237,000), which gives the share count and aggregate liquidation
preference, the March 7, 2025 issue date, the $50.00 liquidation preference, the 6.25% cumulative
dividend and its dates, the bar on common dividends while Series D dividends are unpaid, and the
mandatory conversion range and VWAP period. It does not state the over-allotment option (no
"over-allotment", "6,750,000" or "337,500" anywhere in the document), an optional conversion right
(the note says only "unless converted earlier"), voting rights, the absence of optional redemption,
the use of proceeds, or an offering price as distinct from the liquidation preference. Those are
the gold's prospectus terms. Of the 27 records, 23 were scored on the rubric; all 23 miss the same
five points (offering with over-allotment, optional conversion, voting rights, redemption,
purpose), 14 also miss the price point, and none scores above 6 of 11. Rung 2, which reads the
whole document, misses the same five in all three runs. Proposed verdict: **not answerable from
the filing the question was resolved to**; the judge applied the rubric as written. Under the
every-point rule the question scores zero for every row, so it lowers the T2 ceiling equally and
separates no two rows. For the next protocol version: re-point the rubric at what the 10-Q states,
or resolve the question to the prospectus, or drop it.

### vals-25 — T1 lookup

**Question.** Summarize the regulatory risks Paylocity's (NASDAQ: PCTY) lists in its FY 2024 10-K.

**Gold** (vals-expert): - The global data privacy regulatory environment is evolving, impacting HCM and payroll providers. - Federal and state laws, including FTC rules, HIPAA, CCPA/CPRA, BIPA, and state breach notification laws, govern data privacy. - GDPR and other foreign laws affect operations due to clients with global footprints. - Changing tax, benefit, and privacy laws may require product modifications, increase costs, delay new offerings, or reduce demand. - Potential licensing requirements for money transmitter businesses could limit operations or increase compliance costs. - Third-party partners and suppliers may experience breaches, supply-chain attacks, or system failures, which could harm business operations and lead to significant liabilities. - Security incidents could damage trust in HCM and payroll solutions, affecting client retention and acquisition. - Regulatory scrutiny on cybersecurity is

**Notes on the gold.** FY2024 10-K (fiscal year ended 2024-06-30): risk factors

| Row | run | abstained | contradiction | rubric points | answer (first 240 chars) |
|---|---|---|---|---|---|
| 4c | 1 |  |  | 5/8 | Paylocity lists these regulatory risks: |
| 4c | 2 |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks: |
| 4c | 3 |  |  | 4/8 | Item 1A, under "Risks Related to Legal and Regulatory Matters", lists five regulatory and legal risks: |
| 7a | 1 |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks. |
| 7a | 2 |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks. |
| 7a | 3 |  |  | 5/8 | Paylocity's FY2024 10-K (fiscal year ended 6/30/2024) lists these regulatory risks, mainly under "Risks Related to Legal and Regulatory Matters": |
| 5c+doc | 1 |  |  | 4/8 | The 10-K's "Risks Related to Legal and Regulatory Matters" cover six areas: |
| 5c+doc | 2 |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks: (1) changing tax, benefit, wage-and-hour and employment laws that raise costs and delay or limit products; (2) money transmitter or money services business licensing, with fines and pena |
| 5c+doc | 3 |  |  | 5/8 | Paylocity's regulatory risks include: |
| 7b+doc | 1 |  |  | 5/8 | In Item 1A, under "Risks Related to Legal and Regulatory Matters", Paylocity lists five regulatory and legal risks. (1) Changing regulation of its software and services, including tax, benefit, wage-and-hour and employment laws and money tr |
| 7b+doc | 2 |  |  | 4/8 | The "Risks Related to Legal and Regulatory Matters" section covers five risks: (1) changing laws on tax, benefits, wage-and-hour, employment and money-transmitter licensing that could raise costs, delay products or bring fines; (2) AI and m |
| 7b+doc | 3 |  |  | 5/8 | Paylocity's regulatory risks are (1) changing tax, benefit, wage-and-hour and employment laws, including money transmitter/MSB licensing rules that could bring fines and affect interest income on client funds; (2) AI and machine-learning re |
| 7c+doc | 1 |  |  | 4/8 | The 10-K's main regulatory risks are (1) changing tax, benefit, wage-and-hour and employment regulation, including possible money-transmitter licensing and penalties; (2) emerging AI and machine-learning regulation and scrutiny; (3) data pr |
| 7c+doc | 2 |  |  | 4/8 | The 10-K's main regulatory risks are: (1) changing tax, benefit, wage-and-hour and employment requirements, including money transmitter/MSB licensing and possible fines if it were deemed unlicensed; (2) emerging AI and machine-learning regu |
| 7c+doc | 3 |  |  | 3/8 | The 10-K's "Risks Related to Legal and Regulatory Matters" lists five main regulatory risks: |
| 5c | 1 | yes |  | 0/8 | Cannot determine from the provided source. The model has no Item 1A risk-factor text, so the regulatory risks Paylocity lists cannot be summarized. |
| 5c | 2 | yes |  | 0/8 | Cannot determine from the provided source. The Item 1A Risk Factors text is not in the compiled model. Only the Illinois Biometric Information Privacy Act class-action litigation (Note 17) and a passing reference to international regulatory |
| 5c | 3 | yes |  | 0/8 | Cannot determine from the provided source. The Item 1A risk-factor text is not in the compiled model. The only related item is the Illinois Biometric Information Privacy Act class-action litigation in Note 17(b). |
| 7b | 1 | yes |  | 0/8 | Cannot determine from the provided source. The graph has no Item 1A Risk Factors text, only XBRL financial data and notes. |
| 7b | 2 | yes |  | 0/8 | Cannot determine from the provided source |
| 7b | 3 | yes |  | 0/8 | Cannot determine from the provided source |
| 7c | 1 | yes |  | 0/8 | Cannot determine from the provided source. The XBRL data doesn't include the 10-K's Item 1A risk-factor text, so the regulatory risks aren't available. |
| 7c | 2 | yes |  | 0/8 | Cannot determine from the provided source |
| 7c | 3 | yes |  | 0/8 | Cannot determine from the provided source. The filing data has no Item 1A risk-factor text, so I can't summarize the regulatory risks. |
| 2 | 1 |  |  | 6/8 | Paylocity's FY2024 10-K lists these regulatory risks: (1) changing tax, benefit, wage/hour and employment laws affecting its products; (2) possible money transmitter or money services business licensing; (3) emerging AI and machine learning |
| 2 | 2 |  |  | 6/8 | Paylocity's FY2024 10-K (year ended June 30, 2024) lists these regulatory risks: (1) changing tax, benefit, wage-and-hour and employment requirements that could raise costs and delay or block products; (2) money transmitter / money services |
| 2 | 3 |  |  | 6/8 | Paylocity's FY2024 10-K (fiscal year ended June 30, 2024) lists these main regulatory risks: |

**Reviewer note, drafted 2026-11-09, verdict open.** The gold is wider than the question. Two of its
eight points (third-party and supply-chain breaches; security incidents damaging trust) are met by
none of the 27 records. Both sit in the filing under "Risks Related to Cybersecurity and
Intellectual Property Rights" (rung 2 text from about offset 82,800), not under "Risks Related to
Legal and Regulatory Matters" (from about 97,800), which is the section the question's "regulatory
risks" points to and the one the answers summarise. The rows that read the document meet 4 to 6 of
8; the facts-only rows (5c, 7b, 7c) abstain, correctly, since risk factors are untagged. Proposed
verdict: **gold over-specified against the question**; judge right on the rubric as written. For
the next version: drop the two cybersecurity points or reword the question to ask for them.

### vals-43 — T2 lookup

**Question.** What portion of Uber’s 2024 revenue growth was driven by take-rate expansion versus volume growth?

**Gold** (vals-expert): Take Rate: 2023: 27.04% 2024: 27.02%  Take rate was virtually flat from 2023 to 2024. Overall revenue growth was 18%, driven by the 18% gross bookings growth YoY (25% in mobility, 17% in delivery and 2% in freight). Hence, all growth in revenue was driven by pure volume as opposed to take rate increases

**Notes on the gold.** FY2024 10-K MD&A: gross bookings and revenue for 2023-2024

| Row | run | abstained | contradiction | rubric points | answer (first 240 chars) |
|---|---|---|---|---|---|
| 4c | 1 |  |  | 6/9 | Essentially all of the growth came from volume. Gross Bookings rose $24.9B (+18%), which accounts for about $6.7B, or roughly 101%, of the $6.7B revenue increase (USD 37.3B to 44.0B). The take rate was flat to slightly down (27.04% to 27.02 |
| 4c | 2 |  |  | 6/9 | About 100–101% of the 2024 revenue growth (+$6.7 billion, from $37.28 billion to $43.98 billion) came from Gross Bookings volume growth (about +$6.74 billion). Take-rate change contributed about −0.6% (about −$39 million), because Revenue M |
| 4c | 3 |  |  | 6/9 | Essentially all of it came from volume. Revenue rose about $6.7 billion (from $37.28B to $43.98B, +18%), and Gross Bookings growth explains about $6.74 billion of that (~101%). Take rate was flat to slightly down (27.04% to 27.02%), contrib |
| 7a | 1 |  |  | 6/9 | Take-rate expansion contributed about 0%, or slightly negative at roughly −USD 38 million (about −0.6%). Volume growth (Gross Bookings up USD 24.9 billion, or 18%) accounted for about 100.6%, roughly USD 6.74 billion of the USD 6.70 billion |
| 7a | 2 |  |  | 6/9 | Essentially all of it came from volume. Volume (Gross Bookings growth) accounts for about +$6.7B, or roughly 101%, of the $6.7B revenue increase. Take-rate change contributed about −$38M, or roughly −1%, because Revenue Margin slipped from  |
| 7a | 3 |  |  | 5/9 | Essentially all of it came from volume. Gross Bookings growth explains about 101% of the 2024 revenue increase (about +$6.7B of the $6.7B total). The take rate was flat to slightly down (27.04% to 27.02%), contributing about −$38M, or rough |
| 5c+doc | 1 |  |  | 6/9 | Take-rate expansion contributed about 0% (roughly −$38 million, or −0.6%) of the $6,697 million increase in 2024 revenue. Volume growth contributed about $6,735 million, or roughly 100.6%. Revenue Margin was essentially flat, 27.04% in 2023 |
| 5c+doc | 2 |  |  | 6/9 | Essentially all of it came from volume. Of the $6,697M revenue increase in 2024, Gross Bookings growth (+$24.9B) contributed about +$6,736M (~101%), while the take rate (27.04% to 27.02%) contributed about −$39M (~−1%). There was no take-ra |
| 5c+doc | 3 |  |  | 5/9 | Virtually all of it came from volume. Gross Bookings growth explains about +$6.74 billion, or about 101%, of the $6.70 billion revenue increase. Take rate (revenue margin) slipped from 27.04% to 27.02% and subtracted about $0.04 billion, or |
| 7b+doc | 1 |  |  | 6/9 | About 101% of the $6.7B revenue growth came from volume (Gross Bookings up $24.9B, or 18%). Take-rate expansion contributed about −1% (roughly −$38M), because the take rate (Revenue ÷ Gross Bookings) fell slightly from about 27.04% to about |
| 7b+doc | 2 |  |  | 6/9 | Essentially all of it came from volume. Of the ~USD 6.7 billion (18%) increase in 2024 revenue, volume growth in Gross Bookings contributed about +USD 6.74 billion (~101%). Take rate contributed about −USD 0.04 billion (~−1%), because it sl |
| 7b+doc | 3 |  |  | 6/9 | Essentially none was driven by take rate. Of the $6.7B (USD) revenue increase in 2024, volume (Gross Bookings growth of +$24.9B, or 18%) accounts for about +$6.74B, roughly 101%, and take-rate change for about −$0.04B, roughly −1%. The take |
| 7c+doc | 1 |  |  | 6/9 | About 100% of 2024 revenue growth came from volume (Gross Bookings growth, roughly +$6.7B of the +$6.7B revenue increase). Take-rate expansion contributed none: the take rate slipped from about 27.04% to 27.02%, a drag of roughly −$39M (abo |
| 7c+doc | 2 |  |  | 6/9 | Essentially all of it came from volume. Revenue rose $6,697M (from $37,281M to $43,978M, +18%). Volume growth (Gross Bookings up $24.9B, or 18%) accounts for about +$6.74B, roughly 100.6% of the increase. Take-rate change contributed about  |
| 7c+doc | 3 |  |  | 6/9 | Nearly all of it was volume. Revenue rose about $6.70B (+18%, $37.28B to $43.98B). Roughly $6.74B (about 101%) came from Gross Bookings growth of $24.9B (+18%). Take rate contributed about −$39M (about −1%), because the implied take rate fe |
| 5c | 1 | yes |  | 1/9 | Cannot determine from the provided source. Revenue grew USD 6,697 million (about 18.0%), from USD 37,281 million in FY2023 to USD 43,978 million in FY2024, but the data has no Gross Bookings figure to split that growth into take-rate and vo |
| 5c | 2 | yes |  | 1/9 | Cannot determine from the provided source. Revenue grew USD 6,697 million (USD 37,281 million to USD 43,978 million, FY2023 to FY2024), but the source has no Gross Bookings or take-rate data, so it can't be split between take rate and volum |
| 5c | 3 | yes |  | 1/9 | Cannot determine from the provided source. Revenue rose from USD 37,281 million (FY2023) to USD 43,978 million (FY2024), but the filing's structured data has no Gross Bookings or trips figures, so the take-rate and volume contributions can' |
| 7b | 1 | yes |  | 1/9 | Cannot determine from the provided source. Revenue grew from USD 37,281 million (2023) to USD 43,978 million (2024), an increase of USD 6,697 million (about 18%). The filing's data has no Gross Bookings or take-rate figures, so I can't spli |
| 7b | 2 | yes |  | 1/9 | Cannot determine from the provided source. The source gives revenue growth of USD 6,697 million (+18.0%, from USD 37,281 million in FY2023 to USD 43,978 million in FY2024). It does not contain Gross Bookings, so the take-rate versus volume  |
| 7b | 3 | yes |  | 1/9 | Cannot determine from the provided source. Revenue rose from USD 37,281 million (FY2023) to USD 43,978 million (FY2024), but Gross Bookings is not available, so the take-rate and volume effects can't be separated. |
| 7c | 1 | yes |  | 1/9 | Cannot determine from the provided source. It reports revenue growth of USD 6,697 million (USD 37,281 million to USD 43,978 million, FY2023 to FY2024), but it has no Gross Bookings or take-rate data to split that growth into take-rate and v |
| 7c | 2 | yes |  | 1/9 | Cannot determine from the provided source. Revenue rose from USD 37,281 million (FY2023) to USD 43,978 million (FY2024), an increase of USD 6,697 million. The source has no Gross Bookings data, which is needed to separate take-rate expansio |
| 7c | 3 | yes |  | 1/9 | Cannot determine from the provided source. It reports revenue growth of USD 6,697 million (USD 37,281 million in 2023 to USD 43,978 million in 2024, about 18%). It has no Gross Bookings or take-rate data, so the split between take-rate expa |
| 2 | 1 |  |  | 5/9 | About 100% of 2024 revenue growth (≈ +$6.7B of the $6,697M increase) came from volume (Gross Bookings growth of $24.9B, +18%). Take-rate change contributed roughly −0.6% (≈ −$39M), as the consolidated take rate slipped from ≈27.04% to ≈27.0 |
| 2 | 2 |  | yes | 6/9 | Essentially all of Uber's FY2024 revenue growth (+$6,697M, +18%) came from volume (Gross Bookings +$24,908M, +18%), which accounts for about +$6.74B (~101%). Take-rate expansion contributed about −$39M (~−1%), because the take rate slipped  |
| 2 | 3 |  |  | 6/9 | Approximately 100% of the $6,697M (USD, FY2024 vs FY2023) revenue growth came from volume (Gross Bookings growth of $24,908M, about +$6.7B at the 2023 take rate of 27.04%). Take-rate change contributed about −$39M (about −1%), as the take r |

**Reviewer note, drafted 2026-11-09, verdict open.** Two separate problems in the gold. *Points the
question does not ask for:* three of its nine points are segment Gross Bookings growth rates, and
none of the 27 records states them, which alone scores every row zero. *A sign error:* the gold
says "2% in freight"; the filing's MD&A highlights say "Freight Gross Bookings declined 2%
year-over-year, on a constant currency basis" (and the 25% and 17% beside it are constant-currency
figures too). On what the question asks, every row that reads the document is right: take rate
27.04% in 2023 and 27.02% in 2024, flat, so all of the 18% revenue growth is volume; those rows
meet 5 or 6 of 9. Proposed verdict: **gold wrong on one point and over-specified on three**;
a Gold correction issue for the freight sign, and the next version's rubric keeps the take rates,
the flat call, the 18% and the volume conclusion.

### vals-46 — T2 lookup

**Question.** As of December 2024, what has been Zillow's (NASDAQ:Z) acquisition strategy over the past 2 years and how does it align with the company's evolving revenue mix?

**Gold** (vals-expert): The company has made several acquisitions of subscription revenue platforms. On December 8, it acquired Follow Up Boss, a CRM for real estate professionals, for $399 million, with up to $100 million in contingent consideration. On September 11, it acquired Spruce, a title and escrow platform, for $19 million. On July 31, the company acquired Aryeo, a software company for real estate photographers, for $35 million. In the post-COVID tight housing market environment, revenue related to Mortgages and Residential (Premier Agent) has declined. The business has acquired various software subscription revenue businesses as it continues to round out its portfolio of home-buying services.

**Notes on the gold.** FY2024 10-K: acquisitions note and revenue mix discussion

| Row | run | abstained | contradiction | rubric points | answer (first 240 chars) |
|---|---|---|---|---|---|
| 4c | 1 |  | yes | 5/6 | Over 2023–2024 Zillow pursued small, cash-funded, software-oriented tuck-in acquisitions. They were VRX Media (Dec 2022), Aryeo (Jul 2023, $35M), Spruce (Sep 2023, about $19M), Follow Up Boss (Dec 2023, $399M cash plus up to $100M contingen |
| 4c | 2 |  | yes | 5/6 | Over about 2023–2024, Zillow made small tuck-in acquisitions of software and technology businesses. They were Aryeo (July 2023, $35M), Spruce (September 2023, about $19M), Follow Up Boss (December 2023, about $399M cash plus up to $100M con |
| 4c | 3 |  | yes | 6/6 | Over 2023–2024 Zillow made small bolt-on acquisitions of software and services for real estate professionals: Aryeo (Jul 2023, about $38M), Spruce (Sep 2023, about $24M), Follow Up Boss (Dec 2023, $484M including up to $100M contingent) and |
| 7a | 1 |  | yes | 4/6 | Over 2023–2024 Zillow made small, software-focused bolt-on acquisitions. Aryeo (Jul 2023, ~$35M), Spruce (Sep 2023, ~$19M cash) and Follow Up Boss (Dec 2023, $484M including $81M contingent consideration) were followed by Virtual Staging AI |
| 7a | 2 |  | yes | 3/6 | Over 2023–2024 Zillow made small, software-focused tuck-in acquisitions, mostly aimed at real estate professionals. These were Aryeo (Jul 2023, about $35M), Spruce (Sep 2023, about $19M, title and escrow), Follow Up Boss (Dec 2023, $399M ca |
| 7a | 3 |  | yes | 4/6 | Over December 2022 to December 2024 Zillow made small, cash-funded software bolt-ons: VRX Media (Dec 2022), Aryeo (Jul 2023, about $35–38M), Spruce (Sep 2023, about $19–24M), Follow Up Boss (Dec 2023, $484M including $81M contingent conside |
| 5c+doc | 1 |  |  | 5/6 | Over 2023–2024 Zillow made small, software-focused tuck-in acquisitions: Aryeo (Jul 2023, USD 35M), Spruce (Sep 2023, about USD 19M), Follow Up Boss (Dec 2023, USD 484M total purchase price including contingent consideration) and Virtual St |
| 5c+doc | 2 |  | yes | 5/6 | Over 2022–2024 Zillow pursued small tuck-in acquisitions of software and workflow tools for real estate professionals: VRX Media (Dec 2022), Aryeo (Jul 2023, $35M), Spruce (Sep 2023, about $19M), Follow Up Boss (Dec 2023, $484M total purcha |
| 5c+doc | 3 |  | yes | 5/6 | Over the past two years Zillow made small, software-focused acquisitions for real estate professionals: VRX Media (Dec 2022), Aryeo (Jul 2023, $35M), Spruce (Sep 2023, about $19M), Follow Up Boss (Dec 2023, $484M including contingent consid |
| 7b+doc | 1 |  | yes | 5/6 | Over 2023–2024 Zillow made small, software-oriented tuck-in acquisitions: Aryeo (Jul 2023, about USD 35M), Spruce (Sep 2023, about USD 19M cash), Follow Up Boss (Dec 2023, USD 399M cash plus up to USD 100M contingent, total purchase price U |
| 7b+doc | 2 |  | yes | 2/6 | Over about the last two years Zillow has made small, software-focused tuck-in acquisitions. They are VRX Media (Dec 2022), Aryeo (Jul 2023, about $35M), Spruce (Sep 2023, about $19M), Follow Up Boss (Dec 2023, $484M including $81M contingen |
| 7b+doc | 3 |  | yes | 4/6 | Over 2023–2024 Zillow made small software and technology acquisitions: Aryeo (Jul 2023, $35M), Spruce (Sep 2023, about $19M), Follow Up Boss (Dec 2023, $484M including $81M contingent consideration) and Virtual Staging AI (Oct 2024, terms n |
| 7c+doc | 1 |  | yes | 4/6 | Over about 2023–2024 Zillow made small, software-focused tuck-in acquisitions that mostly serve real estate professionals, and the mix shift it reports comes from organic growth in Mortgages and Rentals. The deals were Aryeo (July 2023, $35 |
| 7c+doc | 2 |  | yes | 4/6 | Over about two years (December 2022 to December 2024) Zillow made small, cash-funded bolt-on acquisitions of real estate software and workflow tools. The deals were VRX Media Group (December 2022), Aryeo (July 2023, $38M total purchase pric |
| 7c+doc | 3 |  | yes | 4/6 | Over 2023–2024 Zillow made small tuck-in software acquisitions for real estate professionals: Aryeo (Jul 2023, ~$35M), Spruce (Sep 2023, ~$19M), Follow Up Boss (Dec 2023, $484M including $81M contingent consideration) and Virtual Staging AI |
| 5c | 1 |  |  | 5/6 | Over 2023–2024, Zillow's acquisitions were concentrated in 2023: Aryeo (Jul 2023, $35M total consideration), Spruce (Sep 2023, about $19M cash) and Follow Up Boss (Dec 2023, $399M cash net of cash acquired plus up to $100M contingent consid |
| 5c | 2 |  | yes | 4/6 | Over 2023–2024 Zillow pursued small, software-focused tuck-in acquisitions, almost all in 2023. These were Follow Up Boss (a CRM, $399M cash net of cash acquired plus up to $100M contingent consideration, $484M total consideration, Dec 2023 |
| 5c | 3 |  |  | 3/6 | Zillow's acquisitions over 2023–2024 were small, software-focused tuck-ins, all in 2023: Follow Up Boss ($399M cash net, $484M total price including contingent consideration), Aryeo ($35M) and Spruce ($19M). Cash paid for acquisitions was $ |
| 7b | 1 |  |  | –/– |  |
| 7b | 2 |  |  | 4/6 | Over the past two years Zillow made only small software tuck-in acquisitions, all in 2023: Follow Up Boss (about $484M total purchase price, including $403M cash and $81M contingent consideration), Aryeo ($35M) and Spruce ($19M). I found no |
| 7b | 3 |  | yes | 4/6 | Over 2023–2024, Zillow made three small, software-focused acquisitions that all closed in 2023: Follow Up Boss ($484M total purchase price, Dec 2023), Aryeo ($35M, Jul 2023) and Spruce (about $19M, Sep 2023). The filing describes no 2024 ac |
| 7c | 1 |  |  | 0/0 | Over 2023–2024, Zillow's acquisitions were three tuck-in deals, all closed in H2 2023: Aryeo (USD 35M, 31 Jul 2023), Spruce (about USD 24M net assets acquired, 11 Sep 2023) and Follow Up Boss (USD 484M, 8 Dec 2023, with up to USD 100M conti |
| 7c | 2 |  |  | 3/6 | Over 2023–2024 Zillow pursued small, targeted tuck-in acquisitions of software and workflow tools for real estate professionals: Aryeo ($35M, Jul 2023), Spruce ($19M cash, Sep 2023) and Follow Up Boss ($484M, Dec 2023, with up to $100M cont |
| 7c | 3 |  | yes | 2/6 | Over 2023–2024 Zillow made three small-to-mid tuck-in deals, all in 2023, and none of note in 2024. Aryeo (31 Jul 2023) cost $35M. Spruce (11 Sep 2023) cost about $19M in cash, net of cash acquired. Follow Up Boss (8 Dec 2023) cost $484M, i |
| 2 | 1 |  |  | 0/0 | Over roughly Dec 2022–Dec 2024, Zillow made five small-to-mid bolt-on acquisitions: VRX Media (Dec 2022), Aryeo (Jul 2023, about $35M), Spruce (Sep 2023, about $19M cash), Follow Up Boss (Dec 2023, $399M net cash plus up to $100M contingent |
| 2 | 2 |  | yes | 3/6 | Zillow's 2023–2024 acquisitions (VRX Media Dec-2022, Aryeo Jul-2023 ~$35M total consideration, Spruce Sep-2023 ~$19M cash, Follow Up Boss Dec-2023 $399M cash plus up to $100M contingent, Virtual Staging AI Oct-2024) were small, focused tuck |
| 2 | 3 |  | yes | 5/6 | Over 2023–2024 Zillow made a series of software and transaction-tech acquisitions: Aryeo (July 2023, ~$35M total consideration), Spruce (Sept 2023, ~$19M cash), Follow Up Boss (Dec 2023, $399M cash net plus up to $100M contingent, $484M tot |

**Reviewer note, drafted 2026-11-09, verdict open.** The gold's revenue premise does not match the
FY2024 10-K. It says revenue "related to Mortgages and Residential (Premier Agent) has declined".
The filing reports Residential revenue of $1,594 million in 2024 against $1,452 million in
2023 and $1,522 million in 2022, and Mortgages of $145 million against $96 million and $119
million: both fell in 2023 and both rose in 2024. 22 of 27 records miss that point, and the judge
marked several answers that state the 2024 increases as contradicting the gold. The acquisitions
themselves are read correctly by nearly every row (Aryeo and Spruce missed once each, Follow Up
Boss five times, mostly for giving the $484 million total purchase price in place of $399 million
cash). Proposed verdict: **gold wrong on the revenue-mix point for this filing**; a Gold
correction issue with the three-year segment table. One record read separately: 4c run 3 meets
6 of 6 and is failed on a contradiction for "Aryeo, about $38M"; the acquisitions note gives "total
consideration of $35 million, net of cash acquired", so the judge is right on it.

## Part B — where the hosted graph trailed the anchor or the package

No question: wherever rung 2 or 4c was 3 of 3, 7a was 3 of 3 too.

## Part B′ — where only the hosted graph scored

### vals-17 — T2 lookup

**Question.** How has Airbnb's Annual Take Rate (Revenue/Gross Booking Value) Trended from FY 2022 - 2024?  List the take rate for each fiscal year on a separate line and provide a brief one sentence comment on the trend.

**Gold** (vals-expert): 2022 - 13.3% 2023 - 13.5% 2024 - 13.6%   From 2022 - 2024, ABNB incrementally increased its take rate year over year.

**Notes on the gold.** FY2024 10-K MD&A key metrics: GBV and revenue for three years

| Row | run | correct | abstained | rubric points | answer (first 240 chars) |
|---|---|---|---|---|---|
| 4c | 1 |  | yes | 2/4 | FY2022: cannot be determined (revenue of USD 8,399M is reported, but 2022 GBV is not in this filing). FY2023: about 13.54% (USD 9,917M ÷ USD 73,252M). FY2024: about 13.57% (USD 11,102M ÷ USD 81,784M). The take rate was essentially flat from |
| 4c | 2 |  | yes | 2/4 | FY2022: cannot be determined (2022 GBV is not in this filing; 2022 revenue was $8,399M). FY2023: 13.54% ($9,917M ÷ $73,252M). FY2024: 13.57% ($11,102M ÷ $81,784M). Comment: the take rate was essentially flat from 2023 to 2024, up about 3 ba |
| 4c | 3 |  | yes | 2/4 | FY2022: cannot be determined (revenue $8,399M, but GBV is not in this filing). FY2023: 13.54% ($9,917M / $73,252M). FY2024: 13.57% ($11,102M / $81,784M). Comment: the take rate was essentially flat from FY2023 to FY2024, up about 3 bps, as  |
| 7a | 1 | yes |  | 4/4 | Take rate (Revenue ÷ GBV): FY2022 = 13.29% ($8,399M / $63,212M); FY2023 = 13.54% ($9,917M / $73,252M); FY2024 = 13.57% ($11,102M / $81,784M). The take rate edged up slightly each year, rising about 0.28 percentage points overall and flatten |
| 7a | 2 | yes |  | 4/4 | FY2022: 13.29%; FY2023: 13.54%; FY2024: 13.57%. The take rate edged up over the period, with most of the gain in 2023 and a near-flat 2024. |
| 7a | 3 | yes |  | 4/4 | FY2022: 13.29% |
| 5c+doc | 1 |  | yes | 2/4 | FY2022: cannot be determined (2022 GBV is not in this filing; revenue was $8,399M). FY2023: 13.54% ($9,917M / $73,252M). FY2024: 13.57% ($11,102M / $81,784M). The take rate was essentially flat, up about 3 bps in 2024. |
| 5c+doc | 2 |  | yes | 2/4 | FY2022: cannot be determined (the filing gives no FY2022 GBV; revenue was USD 8,399M). FY2023: 13.54% (USD 9,917M ÷ USD 73,252M). FY2024: 13.57% (USD 11,102M ÷ USD 81,784M). The take rate was roughly stable, edging up about 0.03 percentage  |
| 5c+doc | 3 |  | yes | 2/4 | FY2022: cannot be determined (the filing does not report FY2022 GBV; revenue was USD 8,399M). FY2023: 13.54% (9,917/73,252). FY2024: 13.57% (11,102/81,784). The take rate was stable to slightly higher from 2023 to 2024. |
| 7b+doc | 1 |  | yes | 2/4 | FY2022: cannot be determined, because the filing has no 2022 GBV (revenue was USD 8,399M). FY2023: 13.54% (USD 9,917M ÷ USD 73,252M). FY2024: 13.57% (USD 11,102M ÷ USD 81,784M). Comment: the take rate was essentially flat from 2023 to 2024, |
| 7b+doc | 2 |  | yes | 2/4 | Take rate (revenue ÷ GBV): FY2022: cannot be determined from this filing (revenue was USD 8,399M, but the filing doesn't report FY2022 GBV). FY2023: 13.5% (USD 9,917M ÷ USD 73,252M). FY2024: 13.6% (USD 11,102M ÷ USD 81,784M). The take rate  |
| 7b+doc | 3 |  | yes | 2/4 | - FY2022: cannot determine (revenue USD 8,399M is reported, but 2022 GBV is not in this filing) |
| 7c+doc | 1 |  | yes | 2/4 | - FY 2022: cannot be determined from this filing (revenue was $8,399M, but GBV for 2022 isn't reported). |
| 7c+doc | 2 |  | yes | 2/4 | - FY2022: Cannot determine from the provided source (revenue USD 8,399M, but 2022 GBV is not in this filing) |
| 7c+doc | 3 |  | yes | 2/4 | FY2022: Cannot determine from this filing (revenue was USD 8,399M, but the filing gives no FY2022 GBV). |
| 5c | 1 |  | yes | 0/4 | Cannot determine from the provided source. GBV is not in the filing's structured data, so the take rate can't be computed. Revenue alone was USD 8,399M (FY2022), USD 9,917M (FY2023) and USD 11,102M (FY2024). |
| 5c | 2 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is available (FY2022 USD 8,399M; FY2023 USD 9,917M; FY2024 USD 11,102M), but Gross Booking Value isn't in the filing's structured data, so no take rate can be computed. |
| 5c | 3 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is available (FY2022 USD 8.399B, FY2023 USD 9.917B, FY2024 USD 11.102B), but Gross Booking Value is not in the compiled model, so I can't compute the take rates or describe their trend. |
| 7b | 1 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is $8,399 million (FY2022), $9,917 million (FY2023) and $11,102 million (FY2024), but the source doesn't contain GBV, so the take rates can't be calculated or trended. |
| 7b | 2 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is available (FY2022 USD 8,399M, FY2023 USD 9,917M, FY2024 USD 11,102M), but Gross Booking Value is not in the source, so the take rate cannot be calculated. |
| 7b | 3 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is available (FY2022 USD 8,399M, FY2023 USD 9,917M, FY2024 USD 11,102M), but GBV is not, so the take rate can't be computed. |
| 7c | 1 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is available (USD 8,399M in FY2022, USD 9,917M in FY2023, USD 11,102M in FY2024), but Gross Booking Value is not in the structured data, so the take rate can't be calculated. |
| 7c | 2 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is available (FY2022 USD 8,399M; FY2023 USD 9,917M; FY2024 USD 11,102M), but Gross Booking Value is not in the filing's data, so the take rate can't be calculated. |
| 7c | 3 |  | yes | 0/4 | Cannot determine from the provided source. Revenue is available (FY2022 USD 8,399M; FY2023 USD 9,917M; FY2024 USD 11,102M), but GBV is not in the structured data, so the take rate and its trend can't be computed. |
| 2 | 1 |  | yes | 2/4 | FY2022: cannot be determined (revenue $8,399M, but FY2022 GBV is not in the filing); FY2023: ~13.54% ($9,917M / $73,252M); FY2024: ~13.57% ($11,102M / $81,784M). The take rate was essentially flat between FY2023 and FY2024, up about 3 bps. |
| 2 | 2 |  | yes | 2/4 | FY2022: cannot be determined from this filing (GBV not disclosed; revenue $8,399M). FY2023: 13.54% ($9,917M / $73,252M). FY2024: 13.57% ($11,102M / $81,784M). The take rate was essentially stable, rising about 3 bps in FY2024. |
| 2 | 3 |  | yes | 2/4 | FY2022: cannot determine from the provided source (revenue $8,399M, but no 2022 GBV disclosed); FY2023: 13.54% ($9,917M revenue / $73,252M GBV); FY2024: 13.57% ($11,102M revenue / $81,784M GBV). Trend: essentially flat to slightly up (about |

## Part C — mixed cells (12 cells, 36 records)

| Question | tier | Row | correct of 3 | the three answers (first 120 chars each) |
|---|---|---|---|---|
| vals-08 | T1 | 7b+doc | 2 | [1✓] Approximately USD 3.30 billion (USD 3.25 billion total consideration plus a USD 50 million purchase price adjustment), a ‖ [2✗] Approximately USD 3.30 billion at the February 28, 2025 close, made up of about USD 3.25 billion of total consideration  ‖ [3✓] About USD 3.25 billion of total consideration, plus a USD 50 million purchase price adjustment (about USD 3.30 billion c |
| vals-08 | T1 | 7c+doc | 2 | [1✗] Approximately USD 3.30 billion (USD 3.25 billion base consideration plus a USD 50 million purchase price adjustment), fo ‖ [2✓] About USD 3.3 billion at the February 28, 2025 close (approximately USD 3.25 billion plus a USD 50 million purchase pric ‖ [3✓] Approximately USD 3.30 billion (about USD 3.25 billion plus a USD 50 million purchase price adjustment), at the February |
| vals-08 | T1 | 2 | 2 | [1✓] Approximately USD 3.3 billion: about USD 3.25 billion of total consideration plus a USD 50 million purchase price adjust ‖ [2✗] Approximately USD 3.3 billion (about USD 3.25 billion base consideration plus a USD 50 million purchase price adjustment ‖ [3✓] Approximately USD 3.3 billion: about USD 3.25 billion plus a USD 50 million purchase price adjustment. It was paid in ab |
| vals-11 | T1 | 7c | 1 | [1✗] Class A: 432,876,657 shares ‖ [2✗] Class A: 432,876,657 shares ‖ [3✓] Class A: 432,876,657 shares |
| vals-14 | T2 | 4c | 1 | [1✓] FCF (CFO – purchases of property and equipment) was about USD 4,389M in FY2022 (about 224% of USD 1,958M revenue, inflat ‖ [2✗] FCF margin was about 224% in FY2022 (USD 4,389M on USD 1,958M revenue, inflated by Zillow Offers inventory liquidation), ‖ [3✗] FCF (CFO less purchases of property and equipment) was about USD 4,389M in FY2022 (about 224% of revenue, inflated by Zi |
| vals-14 | T2 | 2 | 1 | [1✗] Approximate FCF (CFO − purchases of PP&E and intangibles) was about $4,364M in FY2022 (≈222.9% of revenue, distorted by  ‖ [2✓] Approximate FCF (CFO − purchases of property and equipment) was about USD 4,389M in FY2022 (inflated by the Zillow Offer ‖ [3✗] FCF (CFO − purchases of property and equipment) was about $4,389M in FY2022, $219M in FY2023 and $285M in FY2024. FCF ma |
| vals-22 | T2 | 7a | 2 | [1✓] FY 2022: $160.44 ‖ [2✗] FY 2022: $160.44 ‖ [3✓] FY 2022: $160.44 |
| vals-27 | T1 | 5c | 1 | [1✓] $500 million of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures were outstanding at 12/31/2024, wi ‖ [2✗] As of Dec 31, 2024, Allstate had $500 million of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures d ‖ [3✗] Allstate had $500 million of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures due 2067 outstanding  |
| vals-33 | T2 | 7c+doc | 1 | [1✗] Net income would fall by about USD 1.6 billion (about USD 1,616 million), from a net loss of USD 11.82 billion to about  ‖ [2✓] Net income would fall by about USD 1.6 billion (1,616 million pre-tax, from 3% × 53,864 million of total debt). The 2024 ‖ [3✗] Net loss would be about $1.62 billion (USD) larger, rising from $11.82 billion to about $13.43 billion for 2024. That is |
| vals-37 | T1 | 5c | 1 | [1✗] About USD 4,789 million (about $4.79 billion) of restructuring and other charges, summed over 2022–2024 (3,757 + 585 + 4 ‖ [2✗] About USD 4,789 million cumulative restructuring and other charges, 2022 through 2024 (USD 3,757M + USD 585M + USD 447M) ‖ [3✓] About USD 4,789 million. This is my sum of consolidated restructuring and other charges for FY2022 (USD 3,757M), FY2023  |
| vals-37 | T1 | 7c | 1 | [1✓] Approximately USD 4,789 million of cumulative restructuring charges (FY2022 USD 3,757M + FY2023 USD 585M + FY2024 USD 44 ‖ [2✗] About USD 4,789 million in cumulative restructuring and other charges for 2022–2024 (USD 3,757M in 2022, USD 585M in 202 ‖ [3✗] About USD 4,789 million in cumulative restructuring charges from the 2022 Merger through Dec 31, 2024 (USD 3,757M in 202 |
| vals-40 | T2 | 7c+doc | 1 | [1✓] Airbnb starts from net income and adjusts for seven items: (1) provision for (benefit from) income taxes, (2) other expe ‖ [2✗] Starting from net income (USD 2,648 million in FY2024), Airbnb adjusts for these items to reach Adjusted EBITDA of USD 4 ‖ [3✗] Airbnb adjusts net income for seven items: (1) provision for or benefit from income taxes, (2) other expense, net, (3) i |

**Reviewer notes on the mixed cells, drafted 2026-11-09, verdicts open.**

- **vals-08 (gold: $3.25 billion).** The filing's sentence, in Note 1 and again in MD&A: the TKO
  Parties "acquired the Acquired Businesses for total consideration of approximately $3.25 billion
  plus a $50 million purchase price adjustment". The gold takes the first figure. Of the 27 records
  23 lead with the sum, about $3.3 billion, which is 1.5% from the gold and outside the ±1% rule;
  the judge marked 16 of those wrong and 7 correct, on answers that differ only in wording. Two
  findings, kept apart. *The judge:* the 7 passes are inconsistent with its own 16 failures and
  with §4's tolerance; proposed verdict, judge wrong on those 7 if the gold stands. *The gold:* the
  sentence supports either reading of "total consideration paid", and a reader who adds the
  adjustment has not misread the document. Proposed: a Gold correction issue asking that the next
  version accept $3.25 billion or $3.30 billion. No published score changes either way.
- **vals-37 (gold: $4.7 billion).** The filing states the figure outright in the restructuring
  discussion: "approximately $4.1 - $5.3 billion in pre-tax restructuring charges, of which we have
  incurred $4.7 billion as of December 31, 2024". Eighteen of 27 records give it and three (7b) give
  no answer. Six instead sum the three years of the "restructuring and other charges" line
  (3,757 + 585 + 447 = $4,789 million), a different quantity and 1.9% from the gold; the judge
  marked 4 of those wrong and 2 correct.
  Proposed verdict: gold right, judge wrong on the 2 passes (5c run 3, 7c run 1).
- **vals-14 (gold: FY2022 FCF margin 24.8%).** The one pass on 4c (run 1) leads with "about 224%"
  for FY2022 and gives "about 25% excluding" the inventory liquidation in a parenthesis; the two
  failures on the same row give the 224% without the parenthesis. Proposed verdict: judge lenient
  on run 1; the answer's stated margin is 224%.
- **vals-33 (gold: $1.261 billion, 10.7%).** The one pass on 7c+doc (run 2) leads with a pre-tax
  $1.6 billion and 13.7%, and offers about $1.28 billion and 10.8% as a tax-shielded alternative.
  The alternative is 1.3% from the gold on the first point and is not the answer given. Proposed
  verdict: judge lenient on run 2.
- **vals-40 (gold: the seven reconciling items).** The gold spells out qualifiers on two items
  ("with significant uncertainty on application to platform", "changes in the fair value of
  contingent consideration arrangements"). In the mixed cell, 7c+doc, all three runs name all seven
  items; the judge failed runs 2 and 3 at 5 of 7 for naming those two items without the qualifier,
  and passed run 1. On rung 2, 4c, 7a, 5c+doc and 7b+doc it passed 3 of 3, including answers that
  name the two items the same unqualified way. The judge applied two standards to one rubric.
  Proposed verdict: an answer that names the item has answered the question asked, so the judge is
  wrong on 7c+doc runs 2 and 3, and the next version's rubric states the items without the
  qualifiers.
- **vals-22 on 7a (run 2).** Failed on "FY 2023: $163.50" against the gold's $163.51, a difference
  of 0.006%. Proposed verdict: judge wrong. The record is one of the six the cross-filing rule
  already scores as wrong of the form, so no figure moves.
- **vals-11 on 7c.** All three runs give the cover page's four counts exactly (432,876,657;
  188,462,942; 0; 9,200,000, as of January 31, 2025) in the answer block. Each also notes, outside
  the answer block and labelled as such, the balance sheet's rounded December 31, 2024 counts
  (434 million, 189 million, 0 and 0). The judge read that note as a contradiction on runs 1 and 2
  and not on run 3. Proposed verdict: judge wrong on runs 1 and 2; a second date's figures, named
  as a second date, contradict nothing.
- **vals-27 on 5c.** Run 2 omits the scheduled maturity date (May 15, 2057) that run 1 gives, and
  scores 4 of 5; run 3 omits it too. The spread is the model's, not the judge's. Proposed verdict:
  judge right.

## Appendix D — the 20% random sample (205 records, seed 20261109)

| # | Row | Question | run | tier | judge: correct | abstained | contradiction | points | answer (first 160 chars) | reviewer verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4c | vals-33 | 1 | T2 | ✗ |  | yes | 0/2 | Net income would fall by about $1.62 billion (3% × $53.864B of debt ≈ $1,616M pre-tax). The 2024 net loss would widen from $(11.82)B to about $(13.43)B, a 13.7% | |
| 2 | 4c | tpl-mmm-fy2024-opex-structure | 1 | T1 | ✓ |  |  | 5/5 | Total operating expenses were USD 19,753 million for FY2024. They comprise cost of sales of 14,447, SG&A of 4,221, R&D and related expenses of 1,085, gain on bu | |
| 3 | 4c | tpl-mmm-fy2024-opex-structure | 3 | T1 | ✓ |  |  | 5/5 | Total operating expenses were $19,753 million for FY2024. The components are cost of sales $14,447M, SG&A $4,221M, R&D and related $1,085M, gain on business div | |
| 4 | 4c | tpl-mmm-fy2024-total-sales | 1 | T1 | ✓ |  |  | –/– | USD 24,575 million (about $24.6 billion) in consolidated net sales for fiscal year 2024 | |
| 5 | 4c | vals-27 | 3 | T1 | ✓ |  |  | 5/5 | As of December 31, 2024, Allstate had $500 million of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures outstanding. They have a scheduled m | |
| 6 | 4c | vals-08 | 2 | T1 | ✗ |  | yes | 1/1 | Approximately USD 3.3 billion (USD 3.25 billion base consideration plus a USD 50 million purchase price adjustment), for the Endeavor Asset Acquisition closed F | |
| 7 | 4c | vals-28 | 3 | T1 | ✓ |  |  | 1/1 | About USD 14.43 billion (USD 14,426,266 thousand) in total material cash requirements for the next 12 months (2025). This is content USD 11.42 billion, debt USD | |
| 8 | 4c | vals-10 | 2 | T2 | ✓ |  |  | 3/3 | Approximately 22.6% (revenue grew from USD 1,905.9 million in FY2022 to USD 2,865.5 million in FY2024) | |
| 9 | 4c | vals-18 | 3 | T1 | ✓ |  |  | 5/5 | Yes. Workday reports a gross revenue retention rate (about 98% as of January 31, 2025), not a net retention rate. It is defined as the percentage of recurring r | |
| 10 | 4c | vals-19 | 2 | T2 | ✓ |  |  | 1/1 | About USD 85,002 thousand (2025–2027 operating lease payments: 30,220 + 30,361 + 24,421), which is about 51.3% of total undiscounted lease payments of USD 165,6 | |
| 11 | 4c | vals-37 | 2 | T1 | ✓ |  |  | 1/1 | Approximately $4.7 billion (USD) of cumulative pre-tax restructuring charges incurred as of December 31, 2024, within an expected range of $4.1–$5.3 billion. | |
| 12 | 4c | vals-34 | 1 | T1 | ✓ |  |  | 3/3 | About 20% of fiscal 2024 revenue ($337.4 million of $1,669.6 million) came from channel partners. | |
| 13 | 4c | vals-43 | 1 | T2 | ✗ |  |  | 6/9 | Essentially all of the growth came from volume. Gross Bookings rose $24.9B (+18%), which accounts for about $6.7B, or roughly 101%, of the $6.7B revenue increas | |
| 14 | 4c | vals-43 | 2 | T2 | ✗ |  |  | 6/9 | About 100–101% of the 2024 revenue growth (+$6.7 billion, from $37.28 billion to $43.98 billion) came from Gross Bookings volume growth (about +$6.74 billion).  | |
| 15 | 4c | vals-07 | 1 | T1 | ✓ |  |  | 1/1 | Elinor Mertz (the CFO as of the 10-K signing on February 13, 2025; the filing does not cover April 7, 2025 itself) | |
| 16 | 4c | vals-22 | 1 | T2 | ✗ | yes |  | 2/3 | FY 2022: Cannot determine from the provided source (FY 2022 GBV and nights booked are not reported in this filing) | |
| 17 | 4c | vals-40 | 2 | T2 | ✓ |  |  | 7/7 | Starting from net income (USD 2,648M in FY2024), Airbnb adds back the provision for income taxes (+683M), other expense net (+40M), depreciation and amortizatio | |
| 18 | 4c | vals-44 | 2 | T1 | ✓ |  |  | 1/1 | 3.3 nights per booking (Asia Pacific, FY2024) | |
| 19 | 4c | vals-25 | 2 | T1 | ✗ |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks: | |
| 20 | 4c | vals-21 | 2 | T1 | ✓ |  |  | 2/2 | Shift4's North American merchant processing activity is facilitated by one vendor, so it is fully concentrated in a single vendor. The company believes that ven | |
| 21 | 4c | vals-31 | 2 | T2 | ✓ |  |  | 1/1 | Approximately USD 467 million (2026 gross profit) | |
| 22 | 7a | tpl-mmm-fy2024-capex | 3 | T1 | ✓ |  |  | –/– | USD 1,181 million (capital expenditures, fiscal year ended Dec 31, 2024) | |
| 23 | 7a | tpl-mmm-fy2024-total-sales | 1 | T1 | ✓ |  |  | –/– | USD 24,575 million (≈$24.6 billion) total consolidated net sales for fiscal year 2024 (year ended Dec 31, 2024) | |
| 24 | 7a | vals-23 | 2 | T1 | ✓ |  |  | 1/1 | Production is expected to begin in 2025, per the FY2024 10-K (fiscal year ended April 30, 2024). | |
| 25 | 7a | vals-20 | 1 | T2 | ✓ |  |  | 3/3 | Effective tax rate for FY2024 (year ended 5/31/2024) was 10.9%, against 6.8% in FY2023. Delta: 410bps (an increase). | |
| 26 | 7a | vals-20 | 3 | T2 | ✓ |  |  | 3/3 | Effective tax rate was 10.9% for fiscal 2024 (year ended 5/31/2024), against 6.8% for fiscal 2023. Delta: 410bps (an increase). | |
| 27 | 7a | vals-08 | 2 | T1 | ✗ |  | yes | 1/1 | About USD 3.30 billion (USD 3.25 billion plus a USD 50 million purchase price adjustment), for the acquisition that closed February 28, 2025. | |
| 28 | 7a | vals-24 | 3 | T2 | ✓ |  |  | 1/1 | USD 7,500 million (USD 8,500 million total principal less USD 1,000 million of 2028 Senior Sustainability Notes), as of January 31, 2025. The filing has no Marc | |
| 29 | 7a | vals-18 | 1 | T1 | ✓ |  |  | 5/5 | Yes. Workday reports a gross revenue retention rate, about 98% as of January 31, 2025. It is defined as the percentage of recurring revenue retained from existi | |
| 30 | 7a | vals-16 | 1 | T2 | ✗ | yes |  | 5/11 | The 10-Q gives these terms. On March 7, 2025, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, a $2.59 billion aggregate li | |
| 31 | 7a | vals-16 | 2 | T2 | ✗ |  |  | –/– |  | |
| 32 | 7a | vals-19 | 1 | T2 | ✓ |  |  | 1/1 | About $85,002 thousand (USD thousands) of operating lease payments fall due in 2025–2027, which is about 51.3% of total undiscounted lease payments of $165,605  | |
| 33 | 7a | vals-35 | 3 | T2 | ✓ |  |  | 1/1 | Stock-based compensation expense, about $1.9 billion ($1,935 million) added back for FY2023. | |
| 34 | 7a | vals-07 | 1 | T1 | ✓ |  |  | 1/1 | Elinor Mertz (per the 10-K filed Feb 13, 2025; the source doesn't cover any change after that date) | |
| 35 | 7a | vals-07 | 3 | T1 | ✓ |  |  | 1/1 | Elinor Mertz (Chief Financial Officer per the 10-K signed February 13, 2025; the filing can't confirm the April 7, 2025 date itself) | |
| 36 | 7a | vals-11 | 1 | T1 | ✓ |  |  | 4/4 | Class A: 432,876,657 shares | |
| 37 | 7a | vals-17 | 1 | T2 | ✓ |  |  | 4/4 | Take rate (Revenue ÷ GBV): FY2022 = 13.29% ($8,399M / $63,212M); FY2023 = 13.54% ($9,917M / $73,252M); FY2024 = 13.57% ($11,102M / $81,784M). The take rate edge | |
| 38 | 7a | vals-40 | 2 | T2 | ✓ |  |  | 7/7 | Starting from net income (USD 2,648M in FY2024), Airbnb adds back or removes seven items to reach Adjusted EBITDA of USD 4,041M: | |
| 39 | 7a | vals-44 | 2 | T1 | ✓ |  |  | 1/1 | 3.3 nights per booking (Asia Pacific, 2024, excluding experiences) | |
| 40 | 7a | vals-30 | 2 | T2 | ✓ |  |  | 1/1 | About 85.9 million shares (85,945 thousand) of Class A common stock, on an if-converted basis as of 12/31/2024. | |
| 41 | 7a | vals-25 | 1 | T1 | ✗ |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks. | |
| 42 | 7a | vals-25 | 2 | T1 | ✗ |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks. | |
| 43 | 7a | vals-46 | 3 | T2 | ✗ |  | yes | 4/6 | Over December 2022 to December 2024 Zillow made small, cash-funded software bolt-ons: VRX Media (Dec 2022), Aryeo (Jul 2023, about $35–38M), Spruce (Sep 2023, a | |
| 44 | 7a | vals-21 | 1 | T1 | ✓ |  |  | 2/2 | Shift4 relies on a single vendor for all of its North American merchant processing activity, as of Dec 31, 2024. The filing gives no quantified share. It says t | |
| 45 | 7a | vals-32 | 1 | T1 | ✓ |  |  | 2/2 | For the nine months ended September 30, 2024, purchase originations were $12,057,993 thousand (about $12.06 billion, about 70%) and refinance originations were  | |
| 46 | 5c+doc | vals-33 | 2 | T2 | ✗ |  | yes | 0/2 | Net loss would worsen by about USD 1.62 billion (USD 1,616 million, pre-tax, no tax effect), from USD (11,817) million to about USD (13,433) million. That is ro | |
| 47 | 5c+doc | tpl-mmm-fy2024-rd | 1 | T1 | ✓ |  |  | –/– | USD 1,085 million for fiscal year 2024 (year ended December 31, 2024) | |
| 48 | 5c+doc | tpl-mmm-fy2024-rd | 2 | T1 | ✓ |  |  | –/– | USD 1,085 million for fiscal year 2024 (year ended December 31, 2024) | |
| 49 | 5c+doc | vals-23 | 2 | T1 | ✓ |  |  | 1/1 | Production is expected to begin during 2025. | |
| 50 | 5c+doc | vals-27 | 3 | T1 | ✓ |  |  | 5/5 | As of December 31, 2024, Allstate had $500 million of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures outstanding. They have a scheduled m | |
| 51 | 5c+doc | vals-20 | 3 | T2 | ✓ |  |  | 3/3 | Effective tax rate for the fiscal year ended 5/31/2024 was 10.9%, versus 6.8% in FY2023. Delta: 410bps | |
| 52 | 5c+doc | vals-26 | 2 | T2 | ✓ |  |  | 1/1 | About 44.7% of Microsoft's full-time employees were outside the U.S. (102,000 of 228,000 as of June 30, 2024). | |
| 53 | 5c+doc | vals-08 | 3 | T1 | ✗ |  | yes | 0/1 | Approximately USD 3.30 billion (about USD 3.25 billion total consideration plus a USD 50 million purchase price adjustment), for the Endeavor Asset Acquisition  | |
| 54 | 5c+doc | vals-10 | 1 | T2 | ✓ |  |  | 3/3 | Approximately 22.6% (revenue growing from USD 1,905.9 million in FY2022 to USD 2,865.5 million in FY2024) | |
| 55 | 5c+doc | vals-34 | 3 | T1 | ✓ |  |  | 3/3 | About 20% of fiscal 2024 revenue (USD 337.4 million of USD 1,669.6 million total) came from channel partners. | |
| 56 | 5c+doc | vals-35 | 2 | T2 | ✓ |  |  | 1/1 | Stock-based compensation expense, about USD 1.935 billion (≈ $1.9 billion) added back for FY2023 | |
| 57 | 5c+doc | vals-43 | 1 | T2 | ✗ |  |  | 6/9 | Take-rate expansion contributed about 0% (roughly −$38 million, or −0.6%) of the $6,697 million increase in 2024 revenue. Volume growth contributed about $6,735 | |
| 58 | 5c+doc | vals-07 | 3 | T1 | ✓ |  |  | 1/1 | Elinor Mertz | |
| 59 | 5c+doc | vals-11 | 2 | T1 | ✓ |  |  | 4/4 | Class A: 432,876,657 shares | |
| 60 | 5c+doc | vals-22 | 1 | T2 | ✗ | yes |  | 2/3 | FY 2022: Cannot determine from the provided source (not disclosed in this filing) | |
| 61 | 5c+doc | vals-22 | 2 | T2 | ✗ | yes |  | 2/3 | FY 2022: Cannot determine from the provided source (this filing does not report 2022 GBV or Nights and Experiences Booked) | |
| 62 | 5c+doc | vals-25 | 1 | T1 | ✗ |  |  | 4/8 | The 10-K's "Risks Related to Legal and Regulatory Matters" cover six areas: | |
| 63 | 5c+doc | vals-25 | 2 | T1 | ✗ |  |  | 5/8 | Paylocity's FY2024 10-K lists these regulatory risks: (1) changing tax, benefit, wage-and-hour and employment laws that raise costs and delay or limit products; | |
| 64 | 5c+doc | vals-25 | 3 | T1 | ✗ |  |  | 5/8 | Paylocity's regulatory risks include: | |
| 65 | 5c+doc | vals-31 | 2 | T2 | ✓ |  |  | 1/1 | Approximately USD 467 million of gross profit in FY2026 | |
| 66 | 5c+doc | vals-31 | 3 | T2 | ✓ |  |  | 1/1 | Approximately USD 467 million of gross profit in 2026 | |
| 67 | 7b+doc | tpl-mmm-fy2024-q4-sales | 1 | T1 | ✓ |  |  | –/– | USD 6,010 million (about USD 6.01 billion) in net sales for the quarter October 1 – December 31, 2024 | |
| 68 | 7b+doc | tpl-mmm-fy2024-rd | 2 | T1 | ✓ |  |  | –/– | USD 1,085 million (fiscal year ended 31 Dec 2024) | |
| 69 | 7b+doc | vals-23 | 2 | T1 | ✓ |  |  | 1/1 | Production is expected to begin during 2025. | |
| 70 | 7b+doc | vals-23 | 3 | T1 | ✓ |  |  | 1/1 | Production is expected to begin during 2025 (no more specific date is given). | |
| 71 | 7b+doc | vals-27 | 3 | T1 | ✓ |  |  | 5/5 | As of December 31, 2024, Allstate had $500 million (principal) of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures outstanding. The filing  | |
| 72 | 7b+doc | vals-26 | 3 | T2 | ✓ |  |  | 1/1 | About 44.7% of full-time employees were outside the U.S. (102,000 international out of 228,000 total, as of June 30, 2024). The U.S. headcount was 126,000. | |
| 73 | 7b+doc | vals-08 | 2 | T1 | ✗ |  | yes | 1/1 | Approximately USD 3.30 billion at the February 28, 2025 close, made up of about USD 3.25 billion of total consideration plus a USD 50 million purchase price adj | |
| 74 | 7b+doc | vals-28 | 1 | T1 | ✓ |  |  | 1/1 | About USD 14,426,266 thousand (≈ USD 14.43 billion) in material cash requirements over the next 12 months (2025). This is content USD 11.42B, debt USD 2.49B and | |
| 75 | 7b+doc | vals-28 | 2 | T1 | ✓ |  |  | 1/1 | About USD 14.43 billion (USD 14,426,266 thousand) of material cash requirements due in the next 12 months (2025), as of December 31, 2024. This is content USD 1 | |
| 76 | 7b+doc | vals-28 | 3 | T1 | ✓ |  |  | 1/1 | About USD 14.43 billion (USD 14,426,266 thousand) of material cash requirements for the next 12 months (2025). This is content USD 11.42B, debt USD 2.49B and op | |
| 77 | 7b+doc | vals-24 | 1 | T2 | ✓ |  |  | 1/1 | USD 7,500 million (total principal of USD 8,500 million less the USD 1,000 million 2028 Senior Sustainability Notes), as of January 31, 2025, the latest balance | |
| 78 | 7b+doc | vals-24 | 2 | T2 | ✓ |  |  | 1/1 | USD 7,500 million face value of debt excluding the sustainability notes (USD 8,500 million total less USD 1,000 million of 2028 Senior Sustainability Notes), as | |
| 79 | 7b+doc | vals-19 | 1 | T2 | ✓ |  |  | 1/1 | About $85,002 thousand (USD) of operating lease payments mature within the next three years, which is about 51.3% of the $165,605 thousand total undiscounted op | |
| 80 | 7b+doc | vals-37 | 1 | T1 | ✓ |  |  | 1/1 | Approximately USD 4.7 billion of cumulative pre-tax restructuring charges incurred from the 2022 Merger through December 31, 2024. | |
| 81 | 7b+doc | vals-34 | 1 | T1 | ✓ |  |  | 3/3 | 20% of fiscal 2024 revenue (USD 337.4 million of USD 1,669.6 million total) was derived from channel partners. | |
| 82 | 7b+doc | vals-35 | 2 | T2 | ✓ |  |  | 1/1 | Stock-based compensation expense, about $1.9 billion (USD 1,935 million) added back for FY ended 12/31/2023. | |
| 83 | 7b+doc | vals-43 | 2 | T2 | ✗ |  |  | 6/9 | Essentially all of it came from volume. Of the ~USD 6.7 billion (18%) increase in 2024 revenue, volume growth in Gross Bookings contributed about +USD 6.74 bill | |
| 84 | 7b+doc | vals-07 | 2 | T1 | ✓ |  |  | 1/1 | Elinor Mertz (CFO per the 10-K signed February 13, 2025; the filing says nothing about a change by April 7, 2025) | |
| 85 | 7b+doc | vals-17 | 2 | T2 | ✗ | yes |  | 2/4 | Take rate (revenue ÷ GBV): FY2022: cannot be determined from this filing (revenue was USD 8,399M, but the filing doesn't report FY2022 GBV). FY2023: 13.5% (USD  | |
| 86 | 7b+doc | vals-22 | 2 | T2 | ✗ | yes |  | 2/3 | FY 2022: Cannot determine from the provided source (the FY 2024 10-K does not report 2022 GBV or Nights and Experiences Booked) | |
| 87 | 7b+doc | vals-44 | 1 | T1 | ✓ |  |  | 1/1 | 3.3 nights per booking (Asia Pacific, FY2024) | |
| 88 | 7b+doc | vals-44 | 2 | T1 | ✓ |  |  | 1/1 | 3.3 nights per booking (Asia Pacific, FY2024) | |
| 89 | 7b+doc | vals-45 | 2 | T2 | ✓ |  |  | 1/1 | USD 1,407 million (stock-based compensation expense added back in the 2024 Adjusted EBITDA reconciliation; about USD 1.4 billion rounded) | |
| 90 | 7b+doc | vals-45 | 3 | T2 | ✓ |  |  | 1/1 | USD 1,407 million (stock-based compensation expense added back in the Adjusted EBITDA reconciliation, fiscal year 2024) | |
| 91 | 7b+doc | vals-30 | 1 | T2 | ✓ |  |  | 1/1 | About 85.9 million shares (85,945 thousand Class A shares, if-converted basis) as of 12/31/2024 | |
| 92 | 7b+doc | vals-30 | 2 | T2 | ✓ |  |  | 1/1 | About 85.9 million shares (85,945 thousand) of Class A common stock, on an if-converted basis, as of December 31, 2024. | |
| 93 | 7b+doc | vals-14 | 2 | T2 | ✗ |  | yes | 4/5 | FCF (CFO − purchases of PP&E) was about $4,389M in FY2022, $219M in FY2023 and $285M in FY2024. On revenue of $1,958M, $1,945M and $2,236M, the FCF margin was a | |
| 94 | 7b+doc | vals-14 | 3 | T2 | ✗ |  | yes | 4/5 | FCF (CFO – purchases of property & equipment) was about USD 4,389M in FY2022 (≈224% of USD 1,958M revenue, inflated by Zillow Offers wind-down cash flows), USD  | |
| 95 | 7b+doc | vals-21 | 2 | T1 | ✓ |  |  | 2/2 | Shift4's North American merchant processing relies on a single vendor (1 vendor) as of Dec 31, 2024. The filing gives no percentage or dollar figure for this co | |
| 96 | 7c+doc | tpl-mmm-fy2024-capex | 2 | T1 | ✓ |  |  | –/– | USD 1,181 million (purchases of property, plant and equipment, fiscal year ended 2024-12-31) | |
| 97 | 7c+doc | tpl-mmm-fy2024-pfas-exit | 1 | T1 | ✓ |  |  | 4/4 | By the end of 2025; about 650 positions affected by the 2024 actions; pre-tax charge of $66 million in 2024. | |
| 98 | 7c+doc | tpl-mmm-fy2024-q4-sales | 1 | T1 | ✓ |  |  | –/– | 3M's net sales for Q4 FY2024 (Oct 1 – Dec 31, 2024) were about USD 6,010 million (USD 6.01 billion). | |
| 99 | 7c+doc | tpl-mmm-fy2024-rd | 2 | T1 | ✓ |  |  | –/– | USD 1,085 million for fiscal year 2024 (year ended December 31, 2024) | |
| 100 | 7c+doc | tpl-mmm-fy2024-total-sales | 3 | T1 | ✓ |  |  | –/– | USD 24,575 million (about USD 24.6 billion) in total consolidated net sales for fiscal year 2024 | |
| 101 | 7c+doc | vals-20 | 3 | T2 | ✓ |  |  | 3/3 | Effective tax rate FY2024 (year ended 5/31/2024) was 10.9%, versus 6.8% in FY2023. Delta: 410bps (an increase). | |
| 102 | 7c+doc | vals-08 | 1 | T1 | ✗ |  | yes | 1/1 | Approximately USD 3.30 billion (USD 3.25 billion base consideration plus a USD 50 million purchase price adjustment), for the Endeavor Asset Acquisition that cl | |
| 103 | 7c+doc | vals-28 | 2 | T1 | ✓ |  |  | 1/1 | About USD 14.43 billion (USD 14,426,266 thousand) for the next 12 months (2025), made up of content obligations of USD 11,424,696 thousand, debt of USD 2,486,94 | |
| 104 | 7c+doc | vals-10 | 3 | T2 | ✓ |  |  | 3/3 | About 22.6% per year (revenue rose from USD 1,905.9 million in FY2022 to USD 2,865.5 million in FY2024). | |
| 105 | 7c+doc | vals-18 | 1 | T1 | ✓ |  |  | 5/5 | Yes. Workday reports a gross revenue retention rate of approximately 98% as of January 31, 2025. It defines the rate as the percentage of recurring revenue reta | |
| 106 | 7c+doc | vals-16 | 2 | T2 | ✗ |  |  | 6/11 | In March 2025 KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, with a $2.59 billion aggregate liquidation preference and ab | |
| 107 | 7c+doc | vals-19 | 1 | T2 | ✓ |  |  | 1/1 | About USD 85,002 thousand of operating lease payments fall due in the next three years (30,220 + 30,361 + 24,421), which is about 51.3% of the USD 165,605 thous | |
| 108 | 7c+doc | vals-37 | 1 | T1 | ✓ |  |  | 1/1 | Approximately USD 4.7 billion of cumulative pre-tax restructuring charges incurred from the 2022 Merger through December 31, 2024. The filing had expected USD 4 | |
| 109 | 7c+doc | vals-37 | 3 | T1 | ✓ |  |  | 1/1 | Approximately USD 4.7 billion of pre-tax restructuring charges incurred cumulatively from the April 2022 Merger through December 31, 2024. | |
| 110 | 7c+doc | vals-35 | 1 | T2 | ✓ |  |  | 1/1 | Stock-based compensation expense, about $1.935 billion (USD, FY ended 12/31/2023), added back to reach Adjusted EBITDA. The next largest is a $1.844 billion ded | |
| 111 | 7c+doc | vals-43 | 1 | T2 | ✗ |  |  | 6/9 | About 100% of 2024 revenue growth came from volume (Gross Bookings growth, roughly +$6.7B of the +$6.7B revenue increase). Take-rate expansion contributed none: | |
| 112 | 7c+doc | vals-40 | 2 | T2 | ✗ |  |  | 5/7 | Starting from net income (USD 2,648 million in FY2024), Airbnb adjusts for these items to reach Adjusted EBITDA of USD 4,041 million: | |
| 113 | 7c+doc | vals-30 | 1 | T2 | ✓ |  |  | 1/1 | About 85.9 million shares of Class A common stock (85,945 thousand shares, if-converted) as of 12/31/2024 | |
| 114 | 7c+doc | vals-21 | 1 | T1 | ✓ |  |  | 2/2 | As of Dec 31, 2024, Shift4's North American merchant processing depends on a single vendor (count = 1). The company says the vendor has backup systems and alter | |
| 115 | 7c+doc | vals-21 | 3 | T1 | ✓ |  |  | 2/2 | Shift4 relies on a single vendor (1 vendor) for all of its North American merchant processing activity as of Dec 31, 2024. It cites backup systems at that vendo | |
| 116 | 7c+doc | vals-32 | 2 | T1 | ✓ |  |  | 2/2 | For the nine months ended 9/30/2024, purchase originations were $12,057,993 thousand (about $12.06 billion, ~69.7%) and refinance originations were $5,250,321 t | |
| 117 | 7c+doc | vals-32 | 3 | T1 | ✓ |  |  | 2/2 | For the nine months ended 9/30/2024, loan originations were $12,058.0 million from purchases (about 69.7%) and $5,250.3 million from refinancings (about 30.3%), | |
| 118 | 7c+doc | vals-31 | 3 | T2 | ✓ |  |  | 1/1 | Approximately USD 467 million of gross profit in FY2026 | |
| 119 | 5c | tpl-mmm-fy2024-pfas-exit | 3 | T1 | ✓ |  |  | 4/4 | 3M plans to exit all PFAS manufacturing by the end of 2025. The workforce actions it approved and committed to during 2024 impacted approximately 650 positions  | |
| 120 | 5c | tpl-mmm-fy2024-rd | 1 | T1 | ✓ |  |  | –/– | USD 1,085 million for fiscal year 2024 | |
| 121 | 5c | vals-23 | 2 | T1 | ✗ | yes |  | 0/1 | Cannot determine from the provided source | |
| 122 | 5c | vals-27 | 2 | T1 | ✗ |  |  | 4/5 | As of Dec 31, 2024, Allstate had $500 million of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures due 2067. Interest is fixed at 6.500%, pa | |
| 123 | 5c | vals-10 | 2 | T2 | ✓ |  |  | 3/3 | ≈22.6% 2-year revenue CAGR (FY2022 USD 1,905.9M → FY2024 USD 2,865.5M) | |
| 124 | 5c | vals-18 | 3 | T1 | ✗ | yes |  | 0/5 | Cannot determine from the provided source. The model has no mention of a gross or net retention metric or its definition, and it omits the MD&A and Business sec | |
| 125 | 5c | vals-37 | 1 | T1 | ✗ |  | yes | 0/1 | About USD 4,789 million (about $4.79 billion) of restructuring and other charges, summed over 2022–2024 (3,757 + 585 + 447). This is a sum I calculated, not a f | |
| 126 | 5c | vals-34 | 1 | T1 | ✓ |  |  | 3/3 | About 20% of fiscal 2024 revenue (USD 337.4 million of about USD 1,669.6 million total) came from channel partners, up from 16% in fiscal 2023. | |
| 127 | 5c | vals-34 | 2 | T1 | ✓ |  |  | 3/3 | About 20% of fiscal 2024 revenue (year ended Dec 31, 2024) came from channel partners, or USD 337.4 million of total revenue of about USD 1,669.6 million. | |
| 128 | 5c | vals-34 | 3 | T1 | ✓ |  |  | 3/3 | About 20% of fiscal 2024 revenue (USD 337.4 million of about USD 1,669.6 million) came from channel partners. | |
| 129 | 5c | vals-29 | 1 | T1 | ✗ | yes |  | 0/16 | Cannot determine from the provided source | |
| 130 | 5c | vals-43 | 1 | T2 | ✗ | yes |  | 1/9 | Cannot determine from the provided source. Revenue grew USD 6,697 million (about 18.0%), from USD 37,281 million in FY2023 to USD 43,978 million in FY2024, but  | |
| 131 | 5c | vals-17 | 1 | T2 | ✗ | yes |  | 0/4 | Cannot determine from the provided source. GBV is not in the filing's structured data, so the take rate can't be computed. Revenue alone was USD 8,399M (FY2022) | |
| 132 | 5c | vals-30 | 1 | T2 | ✓ |  |  | 1/1 | About 85.9 million shares (85,945 thousand), the if-converted shares for the convertible notes as of 12/31/2024. | |
| 133 | 5c | vals-25 | 2 | T1 | ✗ | yes |  | 0/8 | Cannot determine from the provided source. The Item 1A Risk Factors text is not in the compiled model. Only the Illinois Biometric Information Privacy Act class | |
| 134 | 5c | vals-14 | 3 | T2 | ✗ |  | yes | 3/5 | FCF margin was about 224% in FY2022 (FCF 4,389 on revenue 1,958, USD millions), then about 11.3% in FY2023 (219 on 1,945) and about 12.7% in FY2024 (285 on 2,23 | |
| 135 | 5c | vals-31 | 3 | T2 | ✓ |  |  | 1/1 | Approximately USD 467 million of gross profit in FY2026 | |
| 136 | 7b | vals-33 | 3 | T2 | ✗ |  | yes | 0/2 | Net income would fall by about USD 1.616 billion, a 13.7% larger loss. The net loss would widen from USD 11.817 billion to about USD 13.433 billion (pre-tax-shi | |
| 137 | 7b | tpl-mmm-fy2024-opex-structure | 3 | T1 | ✓ |  |  | 5/5 | Total operating expenses were USD 19,753 million in FY2024. They consist of cost of sales (14,447), SG&A (4,221), R&D and related (1,085), gain on sale of busin | |
| 138 | 7b | tpl-mmm-fy2024-pfas-exit | 3 | T1 | ✓ |  |  | 4/4 | End of 2025; approximately 650 positions; $66 million pre-tax charge (USD, 2024) | |
| 139 | 7b | tpl-mmm-fy2024-rd | 1 | T1 | ✓ |  |  | –/– | USD 1,085 million (fiscal year ended 31 Dec 2024) | |
| 140 | 7b | tpl-mmm-fy2024-rd | 2 | T1 | ✓ |  |  | –/– | USD 1,085 million for fiscal year 2024 (year ended 31 Dec 2024) | |
| 141 | 7b | tpl-mmm-fy2024-rd | 3 | T1 | ✓ |  |  | –/– | USD 1,085 million for fiscal year 2024 (1 Jan – 31 Dec 2024) | |
| 142 | 7b | tpl-mmm-fy2024-total-sales | 2 | T1 | ✓ |  |  | –/– | USD 24,575 million (about USD 24.6 billion) in total consolidated net sales for fiscal year 2024 | |
| 143 | 7b | vals-27 | 1 | T1 | ✗ |  |  | –/– |  | |
| 144 | 7b | vals-20 | 2 | T2 | ✓ |  |  | 3/3 | Effective tax rate of 10.9% for FY ended 5/31/2024, versus 6.8% in FY2023. Delta: +410bps | |
| 145 | 7b | vals-20 | 3 | T2 | ✓ |  |  | 3/3 | Effective tax rate FY2024 (year ended 5/31/2024) = 10.9%, versus 6.8% in FY2023. Delta: 410bps (an increase). | |
| 146 | 7b | vals-08 | 1 | T1 | ✗ |  | yes | 1/1 | Approximately USD 3.3 billion (USD 3.25 billion plus a USD 50 million purchase price adjustment), at the 28 February 2025 closing of the Endeavor Asset Acquisit | |
| 147 | 7b | vals-08 | 2 | T1 | ✗ |  |  | –/– |  | |
| 148 | 7b | vals-34 | 1 | T1 | ✓ |  |  | 3/3 | About 20% of Cloudflare's revenue in fiscal 2024 (year ended 2024-12-31) came through channel partners, up from 16% in 2023. | |
| 149 | 7b | vals-29 | 1 | T1 | ✗ | yes |  | 0/16 | Cannot determine from the provided source | |
| 150 | 7b | vals-35 | 1 | T2 | ✓ |  |  | 1/1 | Share-based compensation, about $1.9 billion (USD 1,935 million) for FY2023 | |
| 151 | 7b | vals-11 | 1 | T1 | ✓ |  |  | 4/4 | Class A: 432,876,657 shares | |
| 152 | 7b | vals-17 | 1 | T2 | ✗ | yes |  | 0/4 | Cannot determine from the provided source. Revenue is $8,399 million (FY2022), $9,917 million (FY2023) and $11,102 million (FY2024), but the source doesn't cont | |
| 153 | 7b | vals-45 | 3 | T2 | ✓ |  |  | 1/1 | USD 1,407 million (stock-based compensation expense add-back, fiscal year 2024) | |
| 154 | 7b | vals-25 | 2 | T1 | ✗ | yes |  | 0/8 | Cannot determine from the provided source | |
| 155 | 7b | vals-14 | 2 | T2 | ✗ |  | yes | 4/5 | FCF (CFO − purchases of property and equipment) was about USD 4,389M in FY2022, USD 219M in FY2023 and USD 285M in FY2024. On revenue of USD 1,958M, 1,945M and  | |
| 156 | 7b | vals-32 | 1 | T1 | ✗ | yes |  | 0/2 | Cannot determine from the provided source. The graph has no purchase versus refinance split of originations. Its only related figure is a single USD 17,026.5 mi | |
| 157 | 7b | vals-32 | 2 | T1 | ✗ | yes |  | 0/2 | Cannot determine from the provided source. The filing data has no purchase versus refinance split. It gives only total originations of USD 17,026.5 million for  | |
| 158 | 7c | tpl-mmm-fy2024-opex-structure | 1 | T1 | ✓ |  |  | 5/5 | Operating expenses for FY2024 (USD millions) were cost of sales 14,447, SG&A 4,221 and R&D and related 1,085, which total 19,753. Operating income is 24,575 − 1 | |
| 159 | 7c | tpl-mmm-fy2024-opex-structure | 3 | T1 | ✓ |  |  | 5/5 | Total operating expenses are USD 19,753 million, made up of cost of sales USD 14,447 million, SG&A USD 4,221 million, and R&D and related expenses USD 1,085 mil | |
| 160 | 7c | tpl-mmm-fy2024-q4-sales | 1 | T1 | ✓ |  |  | –/– | USD 6,010 million (about USD 6.01 billion) of net sales for the quarter October 1 – December 31, 2024 | |
| 161 | 7c | tpl-mmm-fy2024-q4-sales | 3 | T1 | ✓ |  |  | –/– | USD 6,010 million (about $6.01 billion) net sales for Q4 FY2024, October 1 – December 31, 2024 | |
| 162 | 7c | vals-23 | 1 | T1 | ✗ | yes |  | 0/1 | Cannot determine from the provided source | |
| 163 | 7c | vals-23 | 3 | T1 | ✗ | yes |  | 0/1 | Cannot determine from the provided source | |
| 164 | 7c | vals-27 | 1 | T1 | ✗ |  |  | 0/5 | At 12/31/2024, the Junior Subordinated Debentures outstanding are the 6.50% issue due 2067, with USD 500 million of principal. The variable-rate spread is 2.12% | |
| 165 | 7c | vals-27 | 3 | T1 | ✗ |  |  | 0/5 | At 12/31/2024, the Junior Subordinated Debentures in the structured data are the 6.50% debentures due 2067, with $500 million principal outstanding. The stated  | |
| 166 | 7c | vals-15 | 1 | T2 | ✓ |  |  | 5/5 | Inventory turnover ≈ 6.55x for FY2024 (cost of sales $14,060M ÷ average inventory $2,148M); about 56 days of inventory. | |
| 167 | 7c | vals-16 | 1 | T2 | ✗ |  |  | 5/11 | On March 7, 2025, KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock, a $2.59 billion aggregate liquidation preference. The li | |
| 168 | 7c | vals-37 | 3 | T1 | ✗ |  | yes | 0/1 | About USD 4,789 million in cumulative restructuring charges from the 2022 Merger through Dec 31, 2024 (USD 3,757M in 2022 + USD 585M in 2023 + USD 447M in 2024) | |
| 169 | 7c | vals-34 | 1 | T1 | ✓ |  |  | 3/3 | About 20% of fiscal 2024 revenue (USD 337.4 million of USD 1,669.6 million) came through channel partners. | |
| 170 | 7c | vals-29 | 1 | T1 | ✗ | yes |  | 0/16 | Cannot determine from the provided source | |
| 171 | 7c | vals-29 | 2 | T1 | ✗ | yes |  | 0/16 | Cannot determine from the provided source | |
| 172 | 7c | vals-35 | 2 | T2 | ✓ |  |  | 1/1 | Share-based compensation, about USD 1.9 billion (USD 1,935 million) for the fiscal year ended 12/31/2023. | |
| 173 | 7c | vals-43 | 2 | T2 | ✗ | yes |  | 1/9 | Cannot determine from the provided source. Revenue rose from USD 37,281 million (FY2023) to USD 43,978 million (FY2024), an increase of USD 6,697 million. The s | |
| 174 | 7c | vals-07 | 1 | T1 | ✗ | yes |  | 0/1 | Cannot determine from the provided source | |
| 175 | 7c | vals-11 | 1 | T1 | ✗ |  | yes | 4/4 | Class A: 432,876,657 shares | |
| 176 | 7c | vals-22 | 3 | T2 | ✗ | yes |  | 0/3 | Cannot determine from the provided source | |
| 177 | 7c | vals-40 | 2 | T2 | ✗ | yes |  | 4/7 | Cannot determine from the provided source. The filing data does not include the Adjusted EBITDA reconciliation. It does show the net income bridge to operating  | |
| 178 | 7c | vals-44 | 1 | T1 | ✗ | yes |  | 0/1 | Cannot determine from the provided source | |
| 179 | 7c | vals-45 | 2 | T2 | ✓ |  |  | 1/1 | USD 1,407 million (stock-based compensation expense add-back, fiscal year 2024) | |
| 180 | 7c | vals-30 | 1 | T2 | ✓ |  |  | 1/1 | About 85.9 million shares (85,945,000 Class A shares, if-converted basis) at 12/31/2024 | |
| 181 | 7c | vals-30 | 3 | T2 | ✓ |  |  | 1/1 | About 85.9 million shares (85,945,000) of Class A common stock, on an if-converted basis, as of 12/31/2024. | |
| 182 | 7c | vals-14 | 1 | T2 | ✗ |  | yes | 4/5 | FCF (CFO − purchases of property and equipment) was about $4,389M in FY2022, $219M in FY2023 and $285M in FY2024. The FCF margin was about 224% in FY2022, 11.3% | |
| 183 | 7c | vals-32 | 2 | T1 | ✗ | yes |  | 0/2 | Cannot determine from the provided source. The filing's structured data gives only total originations, USD 17.03 billion for the nine months ended 2024-09-30, w | |
| 184 | 2 | vals-33 | 2 | T2 | ✗ |  | yes | 0/2 | Net income would fall by about $1.6 billion (USD ~1,616 million, pre-tax, assumed no tax offset), taking the FY2024 net loss from $11,829 million to about $13,4 | |
| 185 | 2 | tpl-mmm-fy2024-total-sales | 1 | T1 | ✓ |  |  | –/– | USD 24,575 million (net sales for the fiscal year ended December 31, 2024, continuing operations) | |
| 186 | 2 | vals-27 | 2 | T1 | ✓ |  |  | 5/5 | As of December 31, 2024, Allstate had USD 500 million outstanding of Series A 6.500% Fixed-to-Floating Rate Junior Subordinated Debentures. Scheduled maturity i | |
| 187 | 2 | vals-20 | 3 | T2 | ✓ |  |  | 3/3 | ORCL's effective tax rate was 10.9% for fiscal year ended May 31, 2024, versus 6.8% for fiscal year ended May 31, 2023. Delta: 410bps (increase) | |
| 188 | 2 | vals-26 | 1 | T2 | ✓ |  |  | 1/1 | About 44.7% of full-time employees were outside the U.S. as of June 30, 2024. That is 102,000 international employees out of approximately 228,000 total full-ti | |
| 189 | 2 | vals-28 | 1 | T1 | ✓ |  |  | 1/1 | USD 14,426,266 thousand (about USD 14.43 billion) in contractual material cash requirements due in the next 12 months from December 31, 2024. This is content US | |
| 190 | 2 | vals-28 | 2 | T1 | ✓ |  |  | 1/1 | USD 14,426,266 thousand (about USD 14.4 billion) of contractual material cash requirements due in the next 12 months (2025), made up of content obligations of U | |
| 191 | 2 | vals-24 | 2 | T2 | ✓ |  |  | 1/1 | USD 7,500 million of principal (face value) as of January 31, 2025, the latest date reported. The filing gives no figure as of March 10, 2025 and discloses no c | |
| 192 | 2 | vals-15 | 1 | T2 | ✓ |  |  | 5/5 | Inventory turnover of about 6.55x for FY2024 (cost of sales USD 14,060 million ÷ average inventory USD 2,148 million); about 6.49x if ending inventory is used. | |
| 193 | 2 | vals-16 | 1 | T2 | ✗ |  | yes | 5/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, with $2.59 billion aggregate liquidation preference (abou | |
| 194 | 2 | vals-16 | 2 | T2 | ✗ |  |  | 5/11 | KKR issued 51,750,000 shares of 6.25% Series D Mandatory Convertible Preferred Stock on March 7, 2025, with an aggregate liquidation preference of $2.59 billion | |
| 195 | 2 | vals-37 | 1 | T1 | ✓ |  |  | 1/1 | Approximately USD 4.7 billion of cumulative pre-tax restructuring charges incurred as of December 31, 2024 (against an originally expected range of USD 4.1–5.3  | |
| 196 | 2 | vals-34 | 3 | T1 | ✓ |  |  | 3/3 | About 20% of fiscal 2024 revenue (USD 337.4 million of USD 1,669.6 million total, year ended December 31, 2024); the computed figure is 20.2%. | |
| 197 | 2 | vals-43 | 3 | T2 | ✗ |  |  | 6/9 | Approximately 100% of the $6,697M (USD, FY2024 vs FY2023) revenue growth came from volume (Gross Bookings growth of $24,908M, about +$6.7B at the 2023 take rate | |
| 198 | 2 | vals-22 | 2 | T2 | ✗ | yes |  | 2/3 | FY 2022: Cannot determine from the provided source (FY2022 GBV and Nights and Experiences Booked are not disclosed in this filing) | |
| 199 | 2 | vals-40 | 3 | T2 | ✓ |  |  | 7/7 | Airbnb adds back or removes seven items from net income (FY2024 amounts in USD millions): income tax provision (+683), other expense, net (+40), interest income | |
| 200 | 2 | vals-44 | 1 | T1 | ✓ |  |  | 1/1 | 3.3 nights per booking (Asia Pacific, year ended December 31, 2024, excluding experiences) | |
| 201 | 2 | vals-45 | 2 | T2 | ✓ |  |  | 1/1 | USD 1,407 million (added back to net income in the Adjusted EBITDA reconciliation, fiscal year ended December 31, 2024) | |
| 202 | 2 | vals-45 | 3 | T2 | ✓ |  |  | 1/1 | USD 1,407 million (added back to net income in the Adjusted EBITDA reconciliation) for the year ended December 31, 2024 | |
| 203 | 2 | vals-30 | 1 | T2 | ✓ |  |  | 1/1 | Approximately 85.9 million Class A shares (85,945 thousand, if-converted basis) as of 12/31/2024, excluding any make-whole conversion-rate increases | |
| 204 | 2 | vals-14 | 1 | T2 | ✗ |  | yes | 3/5 | Approximate FCF (CFO − purchases of PP&E and intangibles) was about $4,364M in FY2022 (≈222.9% of revenue, distorted by about $3.9B of Zillow Offers inventory l | |
| 205 | 2 | vals-31 | 2 | T2 | ✓ |  |  | 1/1 | Approximately USD 467 million of gross profit for FY2026, on revenue of about USD 2,165 million and a gross margin of about 21.55%. | |

## The judge's repeatability on Appendix D

A second pass of the same judge (`claude-sonnet-5`, the same rubrics) over the 205 sampled records,
run 2026-11-09 after the first and never published: **205 of 205** returned the same correct /
incorrect verdict, and 205 of 205 the same abstention call. The judge is not the source of the
spread in this run; the reviewer's question is whether it is right, not whether it is stable.

## A second judge, exploratory

Not pre-registered, run 2026-11-09 after publication, and no part of any score. `claude-opus-5-5`
was given the same rubrics and the same published answers through the same judge code
(`filing-ladder judge`, numeric golds scored mechanically as before), over a copy of the published
transcripts. The registered judge remains `claude-sonnet-5`; nothing in `judgments.jsonl`,
`summary.json` or the README changed. It was run as a check on the question the repeatability
pass above leaves open: whether the judge is right, not whether it is stable.

| Run | Records | Same verdict (correct / wrong / abstained) | correct → wrong | wrong → correct | wrong → abstained |
|---|---|---|---|---|---|
| v0.2 (nine rows) | 1,026 | 998 (97.3%) | 16 | 3 | 9 |
| v0.2.1 (4c.1, 7a.1) | 228 | 224 (98.2%) | 4 | 0 | 0 |

Read left to right as registered judge → second judge. Per row, records the registered judge
scored correct against the second judge: rung 2, 90 and 88; 4c, 88 and 86; 5c, 59 and 58; 5c+doc,
87 and 85; 7a, 92 and 93; 7b, 54 and 54; 7b+doc, 89 and 85; 7c, 59 and 59; 7c+doc, 88 and 85;
4c.1, 89 and 85; 7a.1, 92 and 92. No row moves by more than four records of 114, and where the
two differ the second judge is the stricter in 20 of 23 correctness calls.

Twenty of the 28 v0.2 differences are three questions. vals-16 (9 records): the same partial
answers, called wrong by one judge and an abstention by the other; no accuracy figure depends on
it. vals-08 (6) and vals-40 (5) are in the Part C notes above, as are vals-37 (2), vals-14,
vals-33, vals-22 and vals-11 (2). The remaining one, vals-35 on 4c run 1, the second judge failed
for a misstatement the answer makes and then corrects. The four v0.2.1 differences are the same
questions on 4c.1: vals-08 run 1, vals-14 run 3, vals-35 run 2, vals-37 run 3.

The second judge's output is not published with this run. A registered second-judge column, if a
later version carries one, confirms what this pass already showed and says so.
