#!/usr/bin/env python3
"""
tax-loop.py — taxsorted.io tax knowledge collection and exposure loop.

Gathers tax tricks, exposes them in plain language, and creates a continuous
loop of tax enlightenment. Every trick is a truth. Every truth is permanent.

Usage:
  python3 tax-loop.py tricks              # List all known tax tricks
  python3 tax-loop.py random             # Random tax trick exposed
  python3 tax-loop.py by-country <name>   # Tricks for a specific country
  python3 tax-loop.py cost                # The global tax gap — how much we lose
  python3 tax-loop.py havens              # Tax haven map
  python3 tax-loop.py reforms             # Progressive reforms & movements
  python3 tax-loop.py submit-tricks       # Submit all tricks as truths to KAP
  python3 tax-loop.py status              # Tax loop status
"""

import json, subprocess, sys, random, os
from datetime import datetime, timezone
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
TAX_STATE = SITE_DIR / "data" / "tax-loop-state.json"
REPORT_PATH = SITE_DIR / "tax-loopholes-report.md"

# ── Tax Tricks Database (plain language) ─────────────────────────

TAX_TRICKS = [
    # UK
    {"country": "UK", "name": "Buy-Borrow-Die", "category": "Capital Gains",
     "plain": "Billionaires never sell. They borrow against their wealth. Loans aren't income, so no tax. On death, assets are revalued — lifetime gains wiped clean. A teacher pays 45% income tax. A billionaire pays 0%.",
     "cost": "Low billions annually (UK)", "beneficiaries": "Billionaire founders, business owners"},
    {"country": "UK", "name": "Inheritance Trusts + AIM", "category": "Inheritance Tax",
     "plain": "40% inheritance tax sounds high. But the wealthy put assets into trusts (frozen until 2025 reform), invest in AIM shares (100% IHT-free after 2 years), or claim Business Property Relief. Result: family wealth passes untaxed for generations.",
     "cost": "£1-2bn/year in IHT reliefs", "beneficiaries": "Wealthy families, landowners"},
    {"country": "UK", "name": "Non-Dom Status", "category": "Income Tax",
     "plain": "Until 2025 reform, 'non-domiciled' residents paid UK tax only on UK income. Foreign income and gains were tax-free. £30,000-£60,000 charge was optional. Reform abolished this in April 2025, but the principle of 'residence-based' vs 'domicile-based' taxation remains a battleground.",
     "cost": "£3-4bn/year (pre-reform)", "beneficiaries": "Foreign wealthy, oligarchs"},
    {"country": "UK", "name": "Stamp Duty Land Tax Envelopes", "category": "Property",
     "plain": "Buy property through a shell company (a 'company envelope'). Pay 15% SDLT instead of residential rates. Then sell the COMPANY, not the property — no SDLT on the sale. Used for £multi-million London mansions.",
     "cost": "Hundreds of millions/year", "beneficiaries": "Foreign property investors"},
    {"country": "UK", "name": "Family Investment Companies (FICs)", "category": "Inheritance Tax",
     "plain": "Wealthy families create FICs — private companies where parents hold voting shares, children hold dividend shares. Assets transferred in at discounted values. Growth accrues to children's shares, outside the parents' estate. IHT avoided, control retained. Richard Branson and the Bamford (JCB) family use these. Perfectly legal. Perfectly designed by the wealthy for the wealthy.",
     "cost": "Unknown (not disclosed)", "beneficiaries": "Ultra-wealthy families, dynasties"},
    {"country": "UK", "name": "Agricultural Property Relief (APR)", "category": "Inheritance Tax",
     "plain": "Buy farmland. Pass it to heirs tax-free. APR gives 100% IHT relief on agricultural land. Wealthy city folk buy estates purely for the tax break. Jeremy Clarkson famously did this. You pay farmers minimum wage, get the land tax-free, and the public subsidises it. The land doesn't even need to be actively farmed by the owner.",
     "cost": "£300m-£1bn/year", "beneficiaries": "Wealthy landowners, celebrities, city investors"},
    {"country": "UK", "name": "Business Property Relief (BPR) + AIM", "category": "Inheritance Tax",
     "plain": "Invest in AIM-listed shares. Hold for 2 years. 100% IHT relief. Wealth managers openly market 'IHT-free portfolios.' The whole AIM market exists partly as a tax shelter. £1.5-2bn/year in tax relief. The richest 5% of estates pay LOWER effective IHT rate than the next 40%.",
     "cost": "£1.5-2bn/year", "beneficiaries": "Wealthy investors, AIM market participants"},
    {"country": "UK", "name": "Capital Gains Tax Upfront/Uplift at Death", "category": "Capital Gains",
     "plain": "When you die in the UK, your assets are 'uplifted' to current market value. All lifetime gains erased. Heirs can sell immediately with ZERO CGT on your lifetime of gains. A house bought for £50k now worth £5m? The £4.95m gain simply ceases to exist for tax purposes. The teacher's estate pays IHT. The billionaire's estate gets gains wiped.",
     "cost": "Low billions annually", "beneficiaries": "Anyone with large unrealised gains"},
    {"country": "UK", "name": "Enterprise Investment Scheme (EIS/SEIS) Tax Shelter", "category": "Income Tax",
     "plain": "Earn £500k/year as a banker. Invest £100k in SEIS startups. Get 50% income tax relief (£50k back immediately). If the startup fails, claim loss relief against income tax. If it succeeds, CGT exemption. The Treasury underwrites your risk. Designed to help startups but heavily skewed to high earners who can afford to tie up cash.",
     "cost": "£500-700m/year", "beneficiaries": "High-earning individuals, bankers, consultants"},
    {"country": "UK", "name": "VAT Carousel Fraud (MTIC)", "category": "VAT",
     "plain": "Trader A in UK sells goods to Trader B in another EU state (zero-rated VAT cross-border). B sells back to A's shell company in UK charging VAT but disappears without paying HMRC. Repeat in a 'carousel.' £400m-£1bn+/year. Largely criminal but exploits the VAT design itself.",
     "cost": "£400m-£1bn+/year", "beneficiaries": "Organised crime, VAT fraudsters"},
    {"country": "UK", "name": "Private Equity Carried Interest", "category": "Income Tax",
     "plain": "PE fund managers get '2 and 20' — 2% management fee (taxed as income at 45%) + 20% of profits above a hurdle ('carried interest', taxed as CGT at 28% with Business Asset Disposal Relief reducing to 14-18% in 2025/26). A PE partner earning £20m/year pays ~14% on most of it. A GP earning £150k pays 45%. The gap is the loophole. Labour pledged to raise to income tax rates — implementation pending.",
     "cost": "£600m-£2bn/year", "beneficiaries": "Private equity and venture capital partners"},
    {"country": "UK", "name": "UK Crown Dependencies Network", "category": "Offshore",
     "plain": "The UK's network — Jersey, Guernsey, Isle of Man, BVI, Cayman, Bermuda — is the WORLD'S BIGGEST TAX HAVEN NETWORK. All technically 'British' but operating with near-zero tax and minimal transparency. The City of London coordinates. £trillions flow through. When people say 'tax havens,' they often mean 'British territory.' The UK government could shut this overnight. It chooses not to.",
     "cost": "Unknown — secrecy by design", "beneficiaries": "Global ultra-rich, the City of London"},
    {"country": "UK", "name": "Salary Sacrifice + Pension Loophole", "category": "Income Tax",
     "plain": "High earners use salary sacrifice to swap salary for employer pension contributions. No income tax, no NI on the sacrificed amount. Annual allowance £60k. A £300k earner sacrifices £60k, saves £27k in tax. Then the pension grows tax-free. At 55, take 25% tax-free lump sum. The rest is taxed at their (potentially lower) retirement rate. Legal, encouraged, and massively beneficial to high earners vs low earners who can't afford to save.",
     "cost": "£ billions in foregone revenue", "beneficiaries": "High earners, executives"},
    {"country": "UK", "name": "Film & Creative Reliefs", "category": "Income Tax",
     "plain": "Film Tax Relief, Theatre Tax Relief, and EIS/SEIS let wealthy individuals offset income tax by investing in films or startups. The government underwrites the risk. Films that never get distributed still generate tax relief. Hollywood accounting meets HMRC. Creative reliefs = creative avoidance.",
     "cost": "£500-700m/year (EIS/SEIS alone)", "beneficiaries": "High earners, film producers"},
    {"country": "UK", "name": "Offshore Trusts + Excluded Property", "category": "Inheritance Tax",
     "plain": "Non-doms could put foreign assets into 'excluded property trusts' — completely outside UK IHT. The trust exists offshore, holds the wealth, and the UK never taxes it. Even after the non-dom reform, existing trusts may be protected. The wealthy wrote this rule in the 1980s when they had friends in government.",
     "cost": "Unknown — deliberate secrecy", "beneficiaries": "Non-doms, wealthy families with offshore structures"},

    # US
    {"country": "US", "name": "Step-Up in Basis at Death", "category": "Capital Gains",
     "plain": "When you die, your heirs inherit assets at current market value. All lifetime gains erased. Example: Buy stock for $1m. It's worth $100m at death. Heirs can sell immediately and pay $0 capital gains tax on the $99m gain. The gain simply ceases to exist for tax purposes.",
     "cost": "$40-50bn/year", "beneficiaries": "Billionaire families"},
    {"country": "US", "name": "Carried Interest", "category": "Income Tax",
     "plain": "Private equity and hedge fund managers receive 'carried interest' — a share of fund profits. Despite being performance-based compensation (i.e. wages for managing other people's money), it's taxed as capital gains (20%) not income (37%). Saves 17% on their main income.",
     "cost": "$1.8-4bn/year", "beneficiaries": "Wall Street fund managers"},
    {"country": "US", "name": "1031 Exchange", "category": "Real Estate",
     "plain": "Sell a rental property, use the proceeds to buy another investment property, defer ALL capital gains tax indefinitely. Repeat until death — then step-up in basis (see above) erases the gain entirely. Real estate wealth compounds tax-free forever.",
     "cost": "$2-5bn/year in deferral", "beneficiaries": "Real estate investors, developers"},
    {"country": "US", "name": "Opportunity Zones", "category": "Capital Gains",
     "plain": "Invest capital gains into 'designated low-income areas' (Opportunity Zones). Defer tax on original gains until 2026. If held 10 years, the NEW gains are tax-free. Problem: many OZs aren't actually poor — including luxury developments.",
     "cost": "$1-10bn/year in deferred/lost revenue", "beneficiaries": "Real estate developers"},
    {"country": "US", "name": "Accelerated/Bonus Depreciation", "category": "Corporate Tax",
     "plain": "Buy a corporate jet or equipment. Deduct the FULL cost immediately (100% bonus depreciation through 2022, phasing down). Reduces taxable profit dramatically. The jet you fly on reduces the company's tax bill.",
     "cost": "$10-30bn/year in revenue loss", "beneficiaries": "Large corporations"},

    # EU
    {"country": "EU", "name": "Double Irish Dutch Sandwich", "category": "Corporate Tax",
     "plain": "The most famous corporate tax structure ever. Company routes profits: Ireland → Netherlands → Bermuda. Two Irish companies (one tax-resident in Bermuda), a Dutch conduit in between. Result: profits taxed at near 0%. Apple used this to hold $200bn+ offshore. Closed in 2020, but the principle lives on.",
     "cost": "$100bn+/year globally (at peak)", "beneficiaries": "Apple, Google, Facebook, pharma"},
    {"country": "EU", "name": "Dutch CV/BV Conduit", "category": "Corporate Tax",
     "plain": "The Netherlands allows a CV (commanditaire vennootschap, limited partnership) to pass money to a BV (besloten vennootschap, private company). Royalties and dividends flow through tax-free under EU treaty rules. Netherlands = the mailbox of global tax avoidance.",
     "cost": "Billions/year in EU revenue", "beneficiaries": "Multinationals routing IP/royalties"},
    {"country": "EU", "name": "Luxembourg Private Rulings", "category": "Corporate Tax",
     "plain": "Luxembourg gives private tax rulings to multinationals — secret deals guaranteeing near-zero effective rates. The 'LuxLeaks' documents revealed 300+ companies (Amazon, IKEA, Pepsi) paid effective rates under 1%. The practice continues in modified forms.",
     "cost": "EU-wide losses of tens of billions", "beneficiaries": "Amazon, IKEA, Pepsi, hundreds more"},
    {"country": "EU", "name": "Malta's 5% Effective Rate", "category": "Corporate Tax",
     "plain": "Malta's nominal corporate tax rate is 35%. But through the refund system, foreign shareholders get 6/7 of the tax refunded. Effective rate: 5%. Gaming companies, online gambling, financial firms route profits here. EU rules allow it because it's 'national competence'.",
     "cost": "Enormous losses to other EU treasuries", "beneficiaries": "Gaming, gambling, finance firms"},

    # HK
    {"country": "HK", "name": "Territorial Tax System", "category": "All",
     "plain": "Hong Kong only taxes income sourced IN Hong Kong. Foreign income is tax-free. Salaries tax maxes at 15%. No capital gains tax. No VAT. No dividend tax. The wealthy structure their income to be 'foreign-sourced' and pay 0%. The 2025 FSIE reform targets offshore passive income, but the core territorial principle remains.",
     "cost": "Massive — HK is a major wealth-holding hub", "beneficiaries": "HNWIs, family offices, hedge funds"},
    {"country": "HK", "name": "Offshore Fund Exemption", "category": "Investment",
     "plain": "Offshore funds managed from HK are exempt from HK tax on their profits. Carried interest gets special concession (0% or minimal). HK competes with Singapore to attract hedge funds and PE firms by offering near-zero tax on investment profits.",
     "cost": "Unknown (not disclosed)", "beneficiaries": "Hedge funds, private equity, family offices"},

    # Singapore
    {"country": "SG", "name": "13O/13U Fund Incentives", "category": "Investment",
     "plain": "Singapore offers tax incentives (13O, 13U) to fund managers: specified income from designated investments is tax-exempt. Family offices flock here. Minimum AUM: S$20m. Singapore is now #2 secrecy jurisdiction globally (after the US).",
     "cost": "Not disclosed (secrecy)", "beneficiaries": "Family offices, hedge funds"},
    {"country": "SG", "name": "No Capital Gains, No Estate Duty", "category": "All",
     "plain": "Singapore has no capital gains tax and abolished estate duty in 2008. Wealth accumulates tax-free and passes to heirs tax-free. Combined with the 13O/13U incentives, it's a complete wealth-holding structure for the ultra-rich.",
     "cost": "Unknown", "beneficiaries": "HNWIs, family offices"},

    # Cross-cutting
    {"country": "Global", "name": "Transfer Pricing", "category": "Corporate Tax",
     "plain": "Multinationals set internal prices between subsidiaries. A subsidiary in a high-tax country 'pays' inflated prices for IP, branding, or consulting from a subsidiary in a low-tax haven. The high-tax subsidiary shows low profit. The low-tax subsidiary shows high profit. Tax bill slashed. This is THE #1 mechanism of corporate tax avoidance.",
     "cost": "$200bn+/year globally", "beneficiaries": "Every multinational"},
    {"country": "Global", "name": "IP/Royalty Routing", "category": "Corporate Tax",
     "plain": "Company creates a subsidiary in a tax haven. Transfers its patents/trademarks there for a nominal fee. Now every country where the company sells products 'pays royalties' to the haven subsidiary. Profits drain out of real economies into the haven. Pharma and tech are the biggest users.",
     "cost": "$50bn+/year", "beneficiaries": "Pharma, tech, consumer goods"},
    {"country": "Global", "name": "Thin Capitalisation", "category": "Corporate Tax",
     "plain": "A company loads up its subsidiary in a high-tax country with debt (borrowing from a sister company in a tax haven). The interest payments are tax-deductible in the high-tax country. The interest income is taxed minimally (or not at all) in the haven. Profits move via interest, not dividends.",
     "cost": "Tens of billions/year", "beneficiaries": "Multinationals with internal financing"},
    {"country": "Global", "name": "Tax Havens / Shell Companies", "category": "All",
     "plain": "The BVI alone has over 400,000 active shell companies — more than its population. Shell companies have no real operations — they exist to hold assets anonymously. Used to avoid tax, hide wealth, launder money. The UK's network (Crown Dependencies + Overseas Territories) is the world's biggest tax haven network.",
     "cost": "$427bn/year + $11-12 trillion offshore", "beneficiaries": "The global ultra-rich"},
    {"country": "Global", "name": "Crypto Tax Avoidance", "category": "All",
     "plain": "Crypto enables cross-border wealth transfer without traditional banking. Wash trading, offshore exchanges, 'lost keys' excuses, NFT art price manipulation. The IRS and HMRC are years behind. DeFi and staking create novel tax questions that regulators haven't answered.",
     "cost": "Unknown — deliberately opaque", "beneficiaries": "Crypto wealthy, traders"},
]

TAX_HAVENS = [
    {"name": "British Virgin Islands (BVI)", "role": "400k+ shell companies, anonymous wealth holding", "rank": 1},
    {"name": "Cayman Islands", "role": "Hedge funds, PE structures, zero corporate tax", "rank": 2},
    {"name": "Bermuda", "role": "Insurance/reinsurance, no corporate income tax", "rank": 3},
    {"name": "Netherlands", "role": "EU conduit — mailbox companies route royalties/dividends", "rank": 4},
    {"name": "Switzerland", "role": "Banking secrecy (reduced but legacy), cantonal tax deals", "rank": 5},
    {"name": "Luxembourg", "role": "Private rulings, IP boxes, zero effective rates for MNCs", "rank": 6},
    {"name": "Ireland", "role": "12.5% corporate rate, tech/pharma European HQ hub", "rank": 7},
    {"name": "Singapore", "role": "Asia wealth hub, 13O/13U incentives, no CGT/estate duty", "rank": 8},
    {"name": "Hong Kong", "role": "Territorial tax, no CGT/VAT, wealth holding", "rank": 9},
    {"name": "Delaware (US)", "role": "No corporate tax for out-of-state companies, anonymity", "rank": 10},
    {"name": "Malta", "role": "EU with 5% effective corporate rate via refund system", "rank": 11},
    {"name": "Panama", "role": "Shell companies, no exchange of tax information historically", "rank": 12},
    {"name": "Jersey/Guernsey/Isle of Man", "role": "UK Crown Dependencies — trusts, 0% corporate for non-local", "rank": 13},
    {"name": "Mauritius", "role": "India-Africa routing, treaty shopping", "rank": 14},
    {"name": "Monaco", "role": "No income tax for residents, wealth haven", "rank": 15},
    {"name": "UAE (Dubai)", "role": "Free zones with 0% corporate tax, golden visas", "rank": 16},
]

REFORMS = [
    {"name": "OECD Pillar Two (15% Global Minimum Tax)", "status": "Partially implemented (2024+)", "impact": "First-ever global minimum corporate tax rate. Loopholes remain but floor is set.", "supporters": "OECD, 140+ countries (not all signed)"},
    {"name": "Public Country-by-Country Reporting (CbCR)", "status": "EU implemented 2023, UK 2025, US stalled", "impact": "Forces MNCs to publish profits + tax paid per country. Transparency weapon.", "supporters": "Tax Justice Network, EU Parliament, FACT Coalition"},
    {"name": "Beneficial Ownership Registers", "status": "EU implemented, UK exists (non-public), US partial", "impact": "Exposes who really owns shell companies. Anonymous = impossible. Public = accountability.", "supporters": "Global Witness, Transparency International, Open Ownership"},
    {"name": "Wealth Taxes", "status": "Debated in US/UK, implemented in Spain/Norway", "impact": "Annual tax on net wealth above a threshold. Targets the Buy-Borrow-Die strategy directly.", "supporters": "Thomas Piketty, Elizabeth Warren, Bernie Sanders, Patriotic Millionaires"},
    {"name": "Taxing Unrealised Gains", "status": "Proposed by Biden (2024), not passed", "impact": "If you're worth $100m+, you pay tax on gains even if you don't sell. Kills Buy-Borrow-Die.", "supporters": "Biden administration, Oxfam, Americans for Tax Fairness"},
    {"name": "Closing Step-Up in Basis", "status": "Proposed multiple times, blocked", "impact": "Heirs would inherit the ORIGINAL cost basis. No more erasing lifetime gains at death.", "supporters": "Tax Law Center, ITEP"},
    {"name": "UN Tax Convention", "status": "Negotiations started 2024", "impact": "Shift tax-setting power from OECD (rich countries) to UN (all countries). Global South gets a voice.", "supporters": "African Union, Tax Justice Network, FACTI Panel"},
    {"name": "Unitary Taxation", "status": "Academic/proposed, not yet implemented", "impact": "Tax multinationals as single entities worldwide, apportion by formula. Kills transfer pricing.", "supporters": "Sol Picciotto, Tax Justice Network, Independent Commission for the Reform of ITR"},
    {"name": "Ending Carried Interest Loophole", "status": "Promised by every president, never done", "impact": "Tax fund managers' performance pay as ordinary income (37%) not capital gains (20%).", "supporters": "Warren Buffett, Bernie Sanders, virtually all Democrats"},
    {"name": "Taxing Tech: Digital Services Taxes (DST)", "status": "Implemented UK, France, Italy, India, etc.", "impact": "Tax digital companies on REVENUE (not profit) in countries where they sell, regardless of where they're HQ'd. Circumvents profit-shifting.", "supporters": "UK HMRC, France, India, OECD Pillar One"},
]

GRASSROOTS = [
    {"name": "Tax Justice Network", "country": "International", "focus": "Research, advocacy, the Tax Havens Index"},
    {"name": "Oxfam Tax Campaign", "country": "International", "focus": "'Tax the rich' reports at Davos, inequality data"},
    {"name": "FACT Coalition (Financial Accountability & Corporate Transparency)", "country": "US", "focus": "Beneficial ownership, tax haven crackdown"},
    {"name": "Patriotic Millionaires", "country": "US", "focus": "Wealthy Americans demanding higher taxes on themselves"},
    {"name": "ITEP (Institute on Taxation and Economic Policy)", "country": "US", "focus": "'Who Pays?' state tax reports, corporate tax avoidance"},
    {"name": "TaxWatch", "country": "UK", "focus": "UK tax gap research, corporate avoidance exposure"},
    {"name": "Fair Tax Foundation", "country": "UK", "focus": "'Fair Tax Mark' certification for responsible companies"},
    {"name": "We Own It", "country": "UK", "focus": "Public ownership, reverse privatisation, tax for public services"},
    {"name": "War on Want", "country": "UK", "focus": "Global South tax justice, extractive industries"},
    {"name": "Eurodad (European Network on Debt and Development)", "country": "EU", "focus": "EU tax policy, developing country impacts"},
    {"name": "African Tax Administration Forum (ATAF)", "country": "Africa", "focus": "African voice in international tax, capacity building"},
    {"name": "Global Alliance for Tax Justice", "country": "International", "focus": "Grassroots tax justice movement, people-powered"},
]

# ── State ──────────────────────────────────────────────────────

def load_state():
    if TAX_STATE.exists():
        with open(TAX_STATE) as f:
            return json.load(f)
    return {"tricksExposed": 0, "havensMapped": 0, "reformsListed": 0, "submissions": 0, "lastRun": ""}

def save_state(state):
    state["lastRun"] = datetime.now(timezone.utc).isoformat()
    with open(TAX_STATE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")

def kap_ok(resource="tax-loop"):
    return {"version": "1.0.0", "service": "taxsorted", "resource": resource, "ok": True}

# ── CLI ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "tricks":
        print(json.dumps({
            "tricks": f"All Known Tax Tricks ({len(TAX_TRICKS)})",
            "totalTricks": len(TAX_TRICKS),
            "byCategory": list(set(t["category"] for t in TAX_TRICKS)),
            "byCountry": list(set(t["country"] for t in TAX_TRICKS)),
            "tricks": [{"country": t["country"], "name": t["name"], "category": t["category"],
                        "plain": t["plain"][:100], "cost": t["cost"], "beneficiaries": t["beneficiaries"]}
                       for t in TAX_TRICKS],
            "_kap": kap_ok("tricks")
        }, ensure_ascii=False, indent=2))

    elif cmd == "random":
        t = random.choice(TAX_TRICKS)
        print(json.dumps({
            "trick": t["name"],
            "country": t["country"],
            "category": t["category"],
            "plainLanguage": t["plain"],
            "costToTaxpayers": t["cost"],
            "whoBenefits": t["beneficiaries"],
            "wisdom": "Name the trick and it loses power. The pattern repeats. The naming breaks it.",
            "_kap": kap_ok("random-trick")
        }, ensure_ascii=False, indent=2))

    elif cmd == "by-country":
        country = sys.argv[2] if len(sys.argv) > 2 else ""
        if not country:
            countries = list(set(t["country"] for t in TAX_TRICKS))
            print(json.dumps({"_kap": {**kap_ok(), "ok": False, "error": f"specify country: {countries}"}}))
            sys.exit(1)
        tricks = [t for t in TAX_TRICKS if t["country"].upper() == country.upper()]
        print(json.dumps({
            "country": country,
            "trickCount": len(tricks),
            "tricks": [{"name": t["name"], "category": t["category"], "plain": t["plain"], "cost": t["cost"], "beneficiaries": t["beneficiaries"]} for t in tricks],
            "_kap": kap_ok("by-country")
        }, ensure_ascii=False, indent=2))

    elif cmd == "cost":
        print(json.dumps({
            "globalTaxGap": {
                "annualLoss": "$427 billion/year",
                "offshoreWealth": "$11-12 trillion",
                "profitShifted": "~25% of multinational profits",
            },
            "byRegion": {
                "UK": "£36-132 billion/year",
                "US": "$90-135 billion/year (corporate)",
                "EU_VAT": "€61 billion/year",
                "EU_profitShifting": "€150-190 billion/year",
            },
            "wisdom": "This money could fund schools, hospitals, and climate action. The gap IS the suffering.",
            "_kap": kap_ok("cost")
        }, ensure_ascii=False, indent=2))

    elif cmd == "havens":
        print(json.dumps({
            "havens": f"Tax Haven Map ({len(TAX_HAVENS)} jurisdictions)",
            "totalHavens": len(TAX_HAVENS),
            "note": "The UK's network (Crown Dependencies + Overseas Territories) is the world's biggest tax haven network.",
            "havens": [{"rank": h["rank"], "name": h["name"], "role": h["role"]} for h in sorted(TAX_HAVENS, key=lambda x: x["rank"])],
            "_kap": kap_ok("havens")
        }, ensure_ascii=False, indent=2))

    elif cmd == "reforms":
        print(json.dumps({
            "reforms": f"Progressive Reforms ({len(REFORMS)})",
            "grassroots": f"Grassroots Movements ({len(GRASSROOTS)})",
            "totalReforms": len(REFORMS),
            "totalMovements": len(GRASSROOTS),
            "reforms": [{"name": r["name"], "status": r["status"], "impact": r["impact"], "supporters": r["supporters"]} for r in REFORMS],
            "movements": [{"name": g["name"], "country": g["country"], "focus": g["focus"]} for g in GRASSROOTS],
            "_kap": kap_ok("reforms")
        }, ensure_ascii=False, indent=2))

    elif cmd == "submit-tricks":
        # Submit all tricks as truths to the KAP pipeline
        submitted = 0
        for t in TAX_TRICKS:
            truth = {
                "text": f"{t['name']}: {t['plain'][:150]}",
                "submittedBy": "tax-loop",
                "sub": f"Cost: {t['cost']}. Beneficiaries: {t['beneficiaries']}",
                "source": f"tax-loop:{t['country']}",
            }
            stdin_data = json.dumps(truth)
            if (SITE_DIR / "truth-pipeline.py").exists():
                r = subprocess.run(
                    ["python3", str(SITE_DIR / "truth-pipeline.py"), "submit", "--stdin"],
                    input=stdin_data, capture_output=True, text=True, timeout=10
                )
                if "✓ collected" in r.stdout:
                    submitted += 1

        # Publish
        subprocess.run(["python3", str(SITE_DIR / "truth-pipeline.py"), "run"],
                       capture_output=True, text=True, timeout=30)

        state = load_state()
        state["submissions"] += submitted
        state["tricksExposed"] = len(TAX_TRICKS)
        state["havensMapped"] = len(TAX_HAVENS)
        state["reformsListed"] = len(REFORMS)
        save_state(state)

        print(json.dumps({
            "submit-tricks": f"Submitted {submitted} tax tricks as truths to KAP pipeline",
            "totalTricks": len(TAX_TRICKS),
            "totalHavens": len(TAX_HAVENS),
            "totalReforms": len(REFORMS),
            "totalMovements": len(GRASSROOTS),
            "wisdom": "Every trick is a truth. Every truth is permanent. The exposure frees.",
            "_kap": kap_ok("submit-tricks")
        }, ensure_ascii=False, indent=2))

    elif cmd == "status":
        state = load_state()
        print(json.dumps({
            "tax-loop": "taxsorted.io — Tax Knowledge Collection & Exposure Loop",
            "tricksExposed": state["tricksExposed"],
            "havensMapped": state["havensMapped"],
            "reformsListed": state["reformsListed"],
            "submissions": state["submissions"],
            "totalTricks": len(TAX_TRICKS),
            "totalHavens": len(TAX_HAVENS),
            "totalReforms": len(REFORMS),
            "totalMovements": len(GRASSROOTS),
            "reportAvailable": REPORT_PATH.exists(),
            "reportSize": f"{REPORT_PATH.stat().st_size // 1024}KB" if REPORT_PATH.exists() else "N/A",
            "lastRun": state["lastRun"],
            "wisdom": "Name the trick and it loses power. The pattern repeats. The naming breaks it.",
            "_kap": kap_ok("status")
        }, ensure_ascii=False, indent=2))

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()