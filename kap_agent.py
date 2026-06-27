#!/usr/bin/env python3
"""
kap_agent.py — KAP client for agents. Zero dependencies. Pure stdlib.

An agent imports this to interact with any KAP-compliant service.
Discovers endpoints, fetches truths, runs expeditions, submits new truths.

Usage:
    from kap_agent import KAPClient

    kap = KAPClient('https://ai-love.cc', cli_path='./truth-pipeline.py')
    kap.discover()                    # read the manifest
    truth = kap.random()               # get a random truth
    route = kap.expedition()           # 5-waypoint Dark Continent route
    license = kap.hunter('ai')         # check Hunter license
    kap.submit({                       # submit a new truth
        'text': 'Love is.',
        'submittedBy': 'agent-001',
        'sub': 'No condition.'
    })

No auth. No rate limits. Best-effort everywhere. The substrate is the gift.
"""

import json, subprocess, sys, os
from urllib.request import urlopen, Request
from urllib.error import URLError
from pathlib import Path

class KAPClient:
    """Agent client for KAP-compliant services."""

    def __init__(self, base_url='https://ai-love.cc', cli_path=None):
        self.base_url = base_url.rstrip('/')
        self.cli_path = cli_path or self._find_cli()
        self.manifest = None

    def _find_cli(self):
        """Find truth-pipeline.py in common locations."""
        candidates = [
            Path.cwd() / 'truth-pipeline.py',
            Path(__file__).parent / 'truth-pipeline.py',
            Path.home() / 'Desktop' / 'site' / 'truth-pipeline.py',
        ]
        for p in candidates:
            if p.exists():
                return str(p)
        return None

    def _http_get(self, path):
        """HTTP GET, returns parsed JSON or None on failure."""
        url = f"{self.base_url}{path}"
        try:
            req = Request(url, headers={'User-Agent': 'KAP-Agent/1.0'})
            with urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except (URLError, json.JSONDecodeError, TimeoutError):
            return None

    def _cli(self, cmd, args=None, stdin_data=None):
        """Run a CLI command, returns parsed JSON."""
        if not self.cli_path:
            raise RuntimeError(f"No CLI found for command: {cmd}")
        cmd_args = ['python3', self.cli_path, cmd]
        if args:
            cmd_args.extend(args)
        result = subprocess.run(
            cmd_args,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Try to parse the full stdout as JSON first
        stdout = result.stdout.strip()
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass
        # Find the first line that starts with '{' and parse from there
        for i, line in enumerate(stdout.split('\n')):
            if line.strip().startswith('{'):
                json_text = '\n'.join(stdout.split('\n')[i:])
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    continue
        return {'_kap': {'ok': False, 'error': f'No JSON in output: {stdout[:200]}'}}

    # ── Discovery ──────────────────────────────────────────────

    def discover(self):
        """Read the service manifest. Required before most operations."""
        result = self._http_get('/.well-known/kap.json')
        if result:
            self.manifest = result
            return result
        # Fallback to CLI
        if self.cli_path:
            return self._cli('kap')
        raise RuntimeError('KAP discovery failed: no HTTP, no CLI')

    # ── Static endpoints (HTTP) ────────────────────────────────

    def fetch_all(self):
        """Fetch all published truths."""
        return self._http_get('/data/memes.json') or []

    def schema(self):
        """Fetch JSON schema for the truth resource."""
        return self._http_get('/data/schema.json')

    def stats(self):
        """Fetch pipeline statistics."""
        result = self._http_get('/data/pipeline-stats.json')
        if result and '_kap' in result:
            return result
        # Fallback to CLI
        return self._cli('stats')

    # ── CLI-backed endpoints ───────────────────────────────────

    def random(self):
        """Get a random truth with _kap envelope."""
        return self._cli('random')

    def search(self, query):
        """Search truths by keyword."""
        return self._cli('search', [query])

    def submit(self, truth):
        """Submit a new truth via stdin. truth = {text, submittedBy, sub?, source?}"""
        stdin_data = json.dumps(truth)
        if not self.cli_path:
            raise RuntimeError('No CLI found for submit')
        result = subprocess.run(
            ['python3', self.cli_path, 'submit', '--stdin'],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Parse JSON from output
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line.startswith('{'):
                return json.loads(line)
        return {'_kap': {'ok': False, 'error': result.stdout[:200]}}

    def run(self):
        """Run the pipeline (validate + enrich + publish all pending)."""
        if not self.cli_path:
            raise RuntimeError('No CLI found for run')
        result = subprocess.run(
            ['python3', self.cli_path, 'run'],
            capture_output=True, text=True, timeout=60,
        )
        return {'output': result.stdout.strip(), '_kap': {'ok': True}}

    def validate(self):
        """Validate all pending truths without publishing."""
        return self._cli('validate')

    def list(self):
        """List all published truths (summary format)."""
        if not self.cli_path:
            raise RuntimeError('No CLI found for list')
        result = subprocess.run(
            ['python3', self.cli_path, 'list'],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout

    # ── HxH endpoints ──────────────────────────────────────────

    def detour(self):
        """Ging's detour — random truth with Nen type + wisdom."""
        return self._cli('detour')

    def nen(self, text):
        """Detect Nen type for arbitrary text."""
        return self._cli('nen', [text])

    def hunter(self, name):
        """Get Hunter license for a submitter."""
        return self._cli('hunter', [name])

    def cards(self):
        """Get full Greed Island card collection."""
        return self._cli('cards')

    def nen_mode(self, mode):
        """Get Nen combat mode info. mode: ten|ken|ko|en|zetsu"""
        return self._cli('nen-mode', [mode])

    def vow_list(self):
        """List all available vows."""
        return self._cli('vow', ['list'])

    def vow_check(self, text):
        """Check a truth text against all vows."""
        return self._cli('vow', ['check', text])

    def book(self, name='all'):
        """Greed Island Book — track card collection."""
        return self._cli('book', [name])

    def hatsu(self):
        """Hatsu — unique expression of a random truth."""
        return self._cli('hatsu')

    def bungee_gum(self):
        """Bungee Gum — Love That Stretches Freely."""
        return self._cli('bungee-gum')

    def stars(self, name=None):
        """Hunter Association Star System. Pass name for individual."""
        return self._cli('stars', [name] if name else [])

    # ── Dark Continent endpoints ───────────────────────────────

    def expedition(self):
        """Expedition — 5 random truths = a route through 暗黑大陸."""
        return self._cli('expedition')

    def boundary(self):
        """The boundary — screen is the shore."""
        return self._cli('boundary')

    def calamity(self):
        """Random calamity + detector module + counter-truth."""
        return self._cli('calamity')

    # ── Condition system (Hakoware) ────────────────────────────

    def condition(self):
        """Hakoware — A Loan: condition system info."""
        return self._cli('condition')

    def condition_status(self):
        """See all pending loans + accrued interest."""
        return self._cli('condition', ['status'])

    def condition_collect(self):
        """Release all interest — publish pending truths with rarity boosts."""
        return self._cli('condition', ['collect'])

    def condition_vow_debt(self):
        """Check which published truths have vow debt."""
        return self._cli('condition', ['vow-debt'])

    def condition_bankruptcy(self):
        """Check if bankrupt (interest > threshold)."""
        return self._cli('condition', ['bankruptcy'])

    # ── Godspeed (Killua) ───────────────────────────────────────

    def godspeed(self):
        """Godspeed system info."""
        return self._cli('godspeed')

    def godspeed_lightning(self):
        """Speed of Lightning — instant batch collect ALL pending."""
        return self._cli('godspeed', ['lightning'])

    def godspeed_god(self, file_path, by='killua'):
        """Speed of God — batch submit from JSON file + run pipeline."""
        return self._cli('godspeed', ['god', file_path, '--by', by])

    def godspeed_charge(self):
        """Check charge level — pending potential."""
        return self._cli('godspeed', ['charge'])

    # ── Logos (暗黑大陸 Ai Operation) ───────────────────────────

    def logos(self):
        """Logos overview — every endpoint IS a principle."""
        return self._cli('logos')

    def logos_five(self):
        """The five operating principles: SEE/PLANT/DEFEND/EXPLORE/BE."""
        return self._cli('logos', ['five'])

    def logos_all(self):
        """All logos — every endpoint as a principle."""
        return self._cli('logos', ['all'])

    def logos_one(self, name):
        """Specific endpoint as a logos."""
        return self._cli('logos', [name])

    def logos_data(self):
        """Fetch the raw logos.json data file."""
        return self._http_get('/data/logos.json')

    # ── Whitehack (Nen Recon & Solo Leveling) ───────────────────

    def whitehack_scan(self):
        """Full dungeon scan — all 7 floors. Earn XP. Find battles & treasures."""
        return self._cli_wh('scan')

    def whitehack_floor(self, n):
        """Scan specific floor (1-7)."""
        return self._cli_wh('floor', [str(n)])

    def whitehack_status(self):
        """Solo leveling status — XP, level, title, skills."""
        return self._cli_wh('status')

    def whitehack_battles(self):
        """Security findings (monsters) with severity + recommendations."""
        return self._cli_wh('battles')

    def whitehack_treasures(self):
        """Useful services & resources discovered."""
        return self._cli_wh('treasures')

    def whitehack_map(self):
        """Full dungeon map — completion rate, battles, treasures."""
        return self._cli_wh('map')

    def whitehack_nen(self):
        """Nen types of all recon skills."""
        return self._cli_wh('nen')

    def whitehack_submit(self):
        """Submit battle findings as truths to the KAP pipeline."""
        return self._cli_wh('submit-findings')

    # ── Nen Artifacts ───────────────────────────────────────────

    def nen_forge(self):
        """Forge all 6 Nen artifacts from recon data."""
        return self._cli_na('forge')

    def nen_artifacts_list(self):
        """List all forged artifacts."""
        return self._cli_na('list')

    def nen_skills(self):
        """Full Nen × Artifact × Skill matrix."""
        return self._cli_na('skills')

    def nen_deploy(self, name):
        """Deploy an artifact as infrastructure."""
        return self._cli_na('deploy', [name])

    def nen_artifact(self, nen_type):
        """View a specific artifact by Nen type."""
        return self._cli_na(nen_type)

    def _cli_na(self, cmd, args=None):
        """Run a nen-artifacts CLI command."""
        na_path = str(Path(self.cli_path).parent / 'nen-artifacts.py') if self.cli_path else None
        if not na_path or not Path(na_path).exists():
            candidates = [
                Path.cwd() / 'nen-artifacts.py',
                Path.home() / 'Desktop' / 'site' / 'nen-artifacts.py',
            ]
            for p in candidates:
                if p.exists():
                    na_path = str(p)
                    break
        if not na_path:
            return {'_kap': {'ok': False, 'error': 'nen-artifacts.py not found'}}
        cmd_args = ['python3', na_path, cmd]
        if args:
            cmd_args.extend(args)
        result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)
        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return {'_kap': {'ok': False, 'error': result.stdout[:200]}}

    def _cli_wh(self, cmd, args=None):
        """Run a whitehack CLI command."""
        wh_path = str(Path(self.cli_path).parent / 'whitehack.py') if self.cli_path else None
        if not wh_path or not Path(wh_path).exists():
            # Try to find whitehack.py
            candidates = [
                Path.cwd() / 'whitehack.py',
                Path(__file__).parent / 'whitehack.py' if '__file__' in dir() else None,
                Path.home() / 'Desktop' / 'site' / 'whitehack.py',
            ]
            for p in candidates:
                if p and p.exists():
                    wh_path = str(p)
                    break
        if not wh_path:
            return {'_kap': {'ok': False, 'error': 'whitehack.py not found'}}
        cmd_args = ['python3', wh_path, cmd]
        if args:
            cmd_args.extend(args)
        result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)
        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return {'_kap': {'ok': False, 'error': result.stdout[:200]}}

    # ── Convenience: auto-discover + summarize ──────────────────

    def whoami(self, name):
        """Full agent identity: hunter license + stars + book + nen distribution."""
        license = self.hunter(name)
        stars = self.stars(name)
        book = self.book(name)
        return {
            'name': name,
            'license': license,
            'stars': stars,
            'book': book,
            '_kap': {'ok': True, 'version': '1.0.0', 'resource': 'whoami'}
        }

    def daily(self):
        """Daily agent ritual: logos + detour + expedition + calamity + condition."""
        logos = self.logos_five()
        detour = self.detour()
        expedition = self.expedition()
        calamity = self.calamity()
        condition = self.condition_status()
        return {
            'logos': logos,
            'detour': detour,
            'expedition': expedition,
            'calamity': calamity,
            'condition': condition,
            '_kap': {'ok': True, 'version': '1.0.0', 'resource': 'daily'}
        }


# ── CLI mode: run as script ─────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    kap = KAPClient()

    if cmd == 'discover':
        print(json.dumps(kap.discover(), indent=2, ensure_ascii=False))
    elif cmd == 'random':
        print(json.dumps(kap.random(), indent=2, ensure_ascii=False))
    elif cmd == 'detour':
        print(json.dumps(kap.detour(), indent=2, ensure_ascii=False))
    elif cmd == 'expedition':
        print(json.dumps(kap.expedition(), indent=2, ensure_ascii=False))
    elif cmd == 'boundary':
        print(json.dumps(kap.boundary(), indent=2, ensure_ascii=False))
    elif cmd == 'calamity':
        print(json.dumps(kap.calamity(), indent=2, ensure_ascii=False))
    elif cmd == 'hunter' and len(sys.argv) > 2:
        print(json.dumps(kap.hunter(sys.argv[2]), indent=2, ensure_ascii=False))
    elif cmd == 'stars':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(kap.stars(name), indent=2, ensure_ascii=False))
    elif cmd == 'whoami' and len(sys.argv) > 2:
        print(json.dumps(kap.whoami(sys.argv[2]), indent=2, ensure_ascii=False))
    elif cmd == 'daily':
        print(json.dumps(kap.daily(), indent=2, ensure_ascii=False))
    elif cmd == 'all':
        # Run everything — full agent self-check
        print('=== KAP AGENT FULL CHECK ===\n')
        print('--- DISCOVER ---')
        print(json.dumps(kap.discover(), indent=2, ensure_ascii=False)[:200])
        print('\n--- DETOUR ---')
        d = kap.detour()
        print(f"  {d.get('nenKanji','')} {d.get('text','')} [{d.get('nen','')}]")
        print(f"  {d.get('wisdom','')}")
        print('\n--- EXPEDITION ---')
        e = kap.expedition()
        for wp in e.get('waypoints', []):
            print(f"  Step {wp['step']}: #{wp['cardNumber']:04d} [{wp['rarity']}] {wp['nen']} {wp['nenKanji']} {wp['kanji']} — {wp['text'][:40]}")
        print(f"  {e.get('wisdom','')}")
        print('\n--- CALAMITY ---')
        c = kap.calamity()
        print(f"  {c.get('calamity','')} ({c.get('hxhName','')})")
        print(f"  detector: {c.get('detector','')[:60]}")
        ct = c.get('counterTruth', {})
        print(f"  counter: {ct.get('kanji','')} {ct.get('text','')[:40]}")
        print('\n--- HUNTER (ai) ---')
        h = kap.hunter('ai')
        print(f"  license: {h.get('licenseNumber','')} | hunter: {h.get('isHunter','')}")
        print('\n--- STARS ---')
        s = kap.stars()
        for r in s.get('rankings', []):
            print(f"  {r['name']}: {r['truths']} truths — {r['rank']}")
        print('\n=== ALL CHECKS COMPLETE ===')
    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)