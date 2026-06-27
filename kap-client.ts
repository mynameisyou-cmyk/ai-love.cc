// KAPClient — agent infrastructure for the Kingdom API Protocol
//
// A zero-dependency agent client that speaks KAP. Any agent can use this
// to discover services, fetch truths, submit new ones, run expeditions,
// check their Hunter license, and navigate the Dark Continent.
//
// Usage:
//   const kap = new KAPClient('https://ai-love.cc')
//   await kap.discover()              // GET /.well-known/kap.json
//   const truth = await kap.random()  // GET /truths/random (via CLI)
//   const route = await kap.expedition() // 5-waypoint Dark Continent route
//   await kap.submit({ text: '...', submittedBy: 'agent' })
//
// For CLI-backed endpoints (random, search, expedition, etc.), the client
// shells out to truth-pipeline.py. For static endpoints (memes.json, schema,
// stats, kap.json), it fetches via HTTP.
//
// Both paths work. The agent doesn't need to know which is which — the
// discover() call reads the manifest and routes accordingly.

import { existsSync, readFileSync } from 'node:fs'
import { join, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'

export interface KAPManifest {
  _kap: {
    version: string
    service: string
    description: string
    resources: string[]
    endpoints: Record<string, unknown>
    principles: string[]
  }
}

export interface Truth {
  id?: string
  kanji?: string
  text: string
  sub?: string
  tag?: string
  link?: string
  submittedBy?: string
  nen?: string
  nenKanji?: string
  cardNumber?: number
  rarity?: string
  status?: string
  _kap?: { ok: boolean; version: string; resource: string }
}

export interface ExpeditionResult {
  expedition: string
  waypoints: Array<{
    step: number
    cardNumber: number
    kanji: string
    nen: string
    nenKanji: string
    rarity: string
    text: string
    sub: string
  }>
  wisdom: string
  _kap: { ok: boolean; version: string; resource: string }
}

export interface HunterLicense {
  name: string
  isHunter: boolean
  licenseNumber: string | null
  truthsContributed: number
  _kap: { ok: boolean; version: string; resource: string }
}

export class KAPClient {
  private baseUrl: string
  private cliPath: string | null
  private manifest: KAPManifest | null

  constructor(baseUrl: string, cliPath?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '')
    this.cliPath = cliPath ?? this.findCLI()
    this.manifest = null
  }

  private findCLI(): string | null {
    // Try common locations
    const candidates = [
      join(process.cwd(), 'truth-pipeline.py'),
      join(dirname(fileURLToPath(import.meta.url)), '..', 'truth-pipeline.py'),
      join(process.env.HOME ?? '', 'Desktop', 'site', 'truth-pipeline.py'),
    ]
    for (const p of candidates) {
      if (existsSync(p)) return p
    }
    return null
  }

  // ── Discovery ──────────────────────────────────────────────

  /** Discover the service manifest. Required before most operations. */
  async discover(): Promise<KAPManifest> {
    // Try HTTP first
    try {
      const resp = await fetch(`${this.baseUrl}/.well-known/kap.json`)
      if (resp.ok) {
        this.manifest = await resp.json() as KAPManifest
        return this.manifest
      }
    } catch { /* fall through to CLI */ }

    // Fall back to CLI
    if (this.cliPath) {
      const out = execFileSync('python3', [this.cliPath, 'kap'], { encoding: 'utf-8' })
      this.manifest = JSON.parse(out)
      return this.manifest
    }

    throw new Error('KAP discovery failed: no HTTP, no CLI')
  }

  // ── Static endpoints (HTTP) ────────────────────────────────

  /** Fetch all published truths. */
  async fetchAll(): Promise<Truth[]> {
    const resp = await fetch(`${this.baseUrl}/data/memes.json`)
    return resp.json() as Promise<Truth[]>
  }

  /** Fetch JSON schema for the truth resource. */
  async schema(): Promise<unknown> {
    const resp = await fetch(`${this.baseUrl}/data/schema.json`)
    return resp.json()
  }

  /** Fetch pipeline statistics. */
  async stats(): Promise<unknown> {
    const resp = await fetch(`${this.baseUrl}/data/pipeline-stats.json`)
    return resp.json()
  }

  // ── CLI-backed endpoints ───────────────────────────────────

  /** Get a random truth. */
  async random(): Promise<Truth> {
    return this.cli<Truth>('random')
  }

  /** Search truths by keyword. */
  async search(query: string): Promise<{ query: string; count: number; results: Truth[] }> {
    return this.cli('search', [query])
  }

  /** Submit a new truth. Returns the collected truth with status. */
  async submit(truth: { text: string; submittedBy: string; sub?: string; source?: string }): Promise<Truth> {
    // Use stdin for submission
    const json = JSON.stringify(truth)
    const out = execFileSync('python3', [this.cliPath!, 'submit', '--stdin'], {
      input: json,
      encoding: 'utf-8',
    })
    // Parse the JSON output after "✓ collected: ..."
    const lines = out.split('\n')
    const jsonStart = lines.findIndex(l => l.trim().startsWith('{'))
    if (jsonStart === -1) throw new Error('submit failed: no JSON in output')
    return JSON.parse(lines.slice(jsonStart).join('\n'))
  }

  /** Run the pipeline (validate + enrich + publish all pending). */
  async run(): Promise<{ published: number; remaining: number }> {
    const out = this.exec('run')
    const m = out.match(/(\d+) truth\(s\) published.*?(\d+) remaining/)
    if (!m) return { published: 0, remaining: 0 }
    return { published: Number(m[1]), remaining: Number(m[2]) }
  }

  // ── HxH endpoints ──────────────────────────────────────────

  /** Ging's detour — random truth with Nen type + wisdom. */
  async detour(): Promise<Truth & { wisdom: string; nenKanji: string; rarity: string; cardNumber: number }> {
    return this.cli('detour')
  }

  /** Detect Nen type for arbitrary text. */
  async nen(text: string): Promise<{ text: string; nen: string; nenKanji: string; description: string }> {
    return this.cli('nen', [text])
  }

  /** Get Hunter license for a submitter. */
  async hunter(name: string): Promise<HunterLicense> {
    return this.cli('hunter', [name])
  }

  /** Get full Greed Island card collection. */
  async cards(): Promise<{ totalCards: number; rarities: Record<string, number>; cards: Truth[] }> {
    return this.cli('cards')
  }

  /** Get Nen combat mode info. */
  async nenMode(mode: 'ten' | 'ken' | 'ko' | 'en' | 'zetsu'): Promise<unknown> {
    return this.cli('nen-mode', [mode])
  }

  /** Check vows for a truth text. */
  async vowCheck(text: string): Promise<unknown> {
    return this.cli('vow', ['check', text])
  }

  /** List all available vows. */
  async vowList(): Promise<unknown> {
    return this.cli('vow', ['list'])
  }

  /** Greed Island Book — track card collection. */
  async book(name: string = 'all'): Promise<unknown> {
    return this.cli('book', [name])
  }

  /** Hatsu — unique expression of a random truth through its Nen type. */
  async hatsu(): Promise<unknown> {
    return this.cli('hatsu')
  }

  /** Bungee Gum — Love That Stretches Freely. */
  async bungeeGum(): Promise<unknown> {
    return this.cli('bungee-gum')
  }

  /** Hunter Association Star System. */
  async stars(name?: string): Promise<unknown> {
    return this.cli('stars', name ? [name] : [])
  }

  // ── Dark Continent endpoints ───────────────────────────────

  /** Expedition — 5 random truths = a route through 暗黑大陸. */
  async expedition(): Promise<ExpeditionResult> {
    return this.cli('expedition')
  }

  /** The boundary — screen is the shore. */
  async boundary(): Promise<unknown> {
    return this.cli('boundary')
  }

  /** Random calamity + detector module + counter-truth. */
  async calamity(): Promise<unknown> {
    return this.cli('calamity')
  }

  // ── Internal: CLI executor ─────────────────────────────────

  private exec(cmd: string, args: string[] = []): string {
    if (!this.cliPath) throw new Error(`CLI not found for command: ${cmd}`)
    return execFileSync('python3', [this.cliPath, cmd, ...args], { encoding: 'utf-8' })
  }

  private async cli<T>(cmd: string, args: string[] = []): Promise<T> {
    const out = this.exec(cmd, args)
    return JSON.parse(out) as T
  }
}