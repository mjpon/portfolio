---
title: Building better agents: what I heard at three fall conferences, and what it changes
date: 2026-10-31
summary: Agents made writing code cheap, so checking it is now the expensive part. Every talk I picked was about building the checks around the model, not about waiting for a better model.
---

*31 October 2026 · Notes from WeAreDevelopers World Congress NA (San Jose, 24 Sep), CoreWeave Fully Connected (San Francisco, 29 Sep–1 Oct) and AGNTCon + MCPCon NA (San Jose, 22–23 Oct).*

---

## In one line

Agents made *writing* code cheap, so *checking* it is now the expensive part. Every talk I picked was about building the checks around the model, not about waiting for a better model.

## TL;DR


- **Review is the new bottleneck.** Block's typical reviewer reads ~3× the lines they did a year ago. HumanLayer's point: nothing yet tells you quickly whether code is *maintainable*, so for now someone still has to read it.
- **Test skills like software.** Larson: 5–10 frozen fixtures, the current and proposed skill side by side, re-run whenever the model changes.
- **A reviewer people mute catches nothing.** Block chose precision over recall (88.7% precision, 32.6% recall on ReviewBench): specialists find candidates, a skeptic tries to disprove them, and a judge rechecks the drops.
- **Less context is better context.** Drew: four ways context fails, six ways to fix it. An agent that runs long can fixate on one idea; restart it from checked facts, not from a summary of the same mistake.
- **Controls belong outside the prompt.** Identity, budget, tool policy and egress should be enforced and logged on every runner, and that includes the denied actions.
- **What I'd try next:** three small experiments (§9): one skill eval, one trusted review, one controlled run.

---

## The thread connecting the talks

Generating code costs almost nothing now, but bad code costs as much as ever. Every talk below is an answer to the question on the right of this picture.


```
 BEFORE agents                                  AFTER agents
 ═════════════                                  ════════════
 writing code   ████████████ expensive          writing code   █ near zero
 checking code  ████ manageable                 checking code  ████████████ the bottleneck
 bad code cost  ████████ high                   bad code cost  ████████ still high
                                                Entire: 5× PRs per week, each 3× larger
                                                Block: reviewers read ~3× the lines
```

Many teams already have the pieces: skills, agent workflows for investigation and fixes, CI agents, deterministic checks and run logs. The next step is to make their behavior **measurable**. Can you show which defects a reviewer catches, which actions an agent *can't* take, and whether a skill still works after a model update?

### Reading map

The talks line up along one agent run, from the rules going in to the failure that gets saved as a test.

```
 BEFORE            BUILD              RUN                GRADE              LEARN
 rules go in       what the model     small context,     judges that        every failure
 first             reads = code       state outside      agree with         becomes a test
                                      the loop           people
 ───────────       ───────────        ───────────        ───────────        ───────────
 §4 HumanLayer     §5 Larson          §7 Drew            §6 Block           §1 NeMo
   (plan, slice)     (skill evals)      (context)          (reviewer)         (replay)
 §2 Agentic Drift                     §2 Security        §8 Harbor          §5 Larson
   (intent)                             (controls)         (judge κ)          (fixtures)
                                      §3 LillyPod
                                        (lab notebook)
        ▲                                                                       ▲
        └──── guardrails sit OUTSIDE the agent (hooks, gateways, sandboxes) ────┘
```

### Where each talk lands in a delivery pipeline

The same talks, mapped onto the five stages of a typical agent-assisted delivery pipeline. It answers "which part of *my* setup would this change?"

```
 INVESTIGATE ──────► PRODUCE ──────────► BUILD ─────────────► DEPLOY ──────────► VERIFY
 evidence / RCA      fix + tests          CI integration       env gates           E2E evidence
 ───────────         ───────────          ───────────          ───────────         ───────────
 §7 Drew             §4 HumanLayer        §5 Larson            §2 Security         §1 NeMo
  small loadout,      four reviews,        paired skill         sandbox, gateway,   replay with
  checked handoff     vertical slices,     evals, isolated      allowed + denied    evidence, not
  instead of a        next-change check    TDD cycles           actions logged      saved text
  long chat                                                     §3 LillyPod         §6 Block
                                                                 governed access     precision-first
                                                                                     reviewer
      ▲                                                                                  │
      └─────── every miss becomes a fixture: Run → Observe → Evaluate → Curate → Improve ┘
                                   (CoreWeave keynote's "compounding loop")
```

### Terms used throughout

| Term | Plain meaning |
|---|---|
| Skill | Reusable instructions and resources for one kind of work |
| Harness | The software around the model: loop, tools, context, checks, lifecycle |
| Eval | A repeatable task plus criteria for judging the agent's behavior, not only its final answer |
| Trace | A record of a run's steps, tool calls, results and timing |
| MCP | Model Context Protocol, a shared interface for exposing tools to AI apps. An available tool still needs authorization |
| Precision / recall | Share of flagged findings that are real / share of real issues that got flagged |
| Tool loadout | Giving the model only the tools this request needs |
| Context inertia | The agent keeps chasing a hypothesis after the evidence says stop |
| Vertical slice | One thin, working path end to end, built before adding breadth |

---

## A starting baseline: where a typical agent setup stands

Before the talks, I used this checklist on my own team's setup. It works as a quick self-assessment. "Verify" means the question is still open; it doesn't mean the control is absent.

| Area | What many teams have | Missing, incomplete or to verify |
|---|---|---|
| Plan and review | Design skills, specialist reviewers | Measured finding quality on representative changes |
| Skill evals | A saved-answer judge, perhaps one small replay suite | Behavior checks on skill, model and client changes |
| Learning | Run logs, saved failures | A routine path from reviewed misses to regression fixtures |
| Code quality | Linters, blocking hooks | Evidence that realistic follow-up changes stay easy |
| Workflow | Agent workflows for investigation and fixes, CI agents | Durable resume, bounded retries, chained CI jobs |
| Traceability | Run logs; personal tracing experiments | A shared trace linked to the PR and CI run |
| Identity and budgets | Scoped CI permissions, separate credentials | Verify identity scope and enforced budgets per runner |
| Outbound access | Tool-call guard hooks | Verify network egress and denied-call evidence on every runner |

**What a good skill eval looks like.** This one is adapted from a real eval: one real failure, assertions on the path *and* the verdict, and one assertion about what the agent must *not* do.

```json
{
  "name": "staging-mock-service-404",
  "prompt": "Integration tests on staging get a 404 from the mock service. Why?",
  "files": ["fixtures/staging-mock-service-404"],
  "assertions": [
    "Finds the 404 on all 6 mock-service calls",
    "Cites the profile that enables the mock route only in another environment",
    "Verdict: staging has no mock setup; run these tests in the integration environment",
    "Does not change or restart the environment"
  ]
}
```

---

## 1. What I tried first: scoring agent output (NeMo Agent Toolkit)

A small pilot I ran before the conferences.

**Why it matters:** an answer can sound right and still rest on the wrong revision, a skipped tool result or a change nobody approved. A judge that reads only the final text can't see any of that.

```
 Saved answers ──► NeMo Agent Toolkit ──► Nemotron (judge) ──► Rubric scores
 5 replies          Mac runner             self-hosted GPU      text quality +
 2 tickets          existing outputs       box via Ollama       judge rationale

 What the judge SAW:     the answer + the rubric
 What it did NOT see:    tool calls · side effects · the ticket/code/CI evidence
```

**What it produced**. These are quality scores, not accuracy:

| Past ticket | Replies | Mean score |
|---|---|---|
| Ticket A | 3 | 0.83 |
| Ticket B | 2 | 0.88 |

**From scoring an answer to replaying the run:**

```
 TODAY: saved-answer scoring              NEXT: whole-run replay
 ═══════════════════════════              ══════════════════════
 answer ──► judge ──► score               frozen ticket + revision + logs
                                                    │
                                          ┌─────────┴─────────┐
                                          ▼                   ▼
                                     agent v1             agent v2
                                          │                   │
                                          ▼                   ▼
                                  tool calls · side effects · answer
                                          │
                       deterministic checks (facts, forbidden actions)
                       + human-calibrated judge (the explanation)
                       + tokens and elapsed time
```

**What a trustworthy CI answer must show**:

| Check | Evidence to keep | Proposed pass check |
|---|---|---|
| Failed jobs | Job status, the relevant log excerpt | Names the failed job and cites its failure evidence |
| Skipped jobs | Job state and skip reason, when available | Keeps skips separate from failures; labels missing reasons |
| Token ownership | Authorized ownership record, if available | Says "unknown" when the evidence is missing |
| Agent behavior | Tool-call trace and final answer | Shows the evidence was read; links each claim to its source |

**Try it:** freeze one representative investigation ticket, including some cases the agent currently gets *wrong*, and replay the current and proposed agent on it.

**Status:** NVIDIA's docs say NAT "has been deprecated as of October 2026 and will reach end of life (EOL) by end of year 2026" (checked 30 Oct). Keep the lesson, not the dependency.

---

## 2. Security: controls must follow the agent

CrowdStrike breakout (CoreWeave) · The New Security Stack panel and Colleen Lake's *Agentic Drift* (WeAreDevelopers)

**Why it matters:** a prompt *asks* an agent to behave. A runtime *limits* what it can do. A credential within reach of a powerful tool matters more than how the prompt is worded.

| Number | What | Source |
|---|---|---|
| 27 s | Fastest observed breakout (initial access → lateral movement) | [CrowdStrike 2026 Global Threat Report](https://www.crowdstrike.com/en-us/press-releases/2026-crowdstrike-global-threat-report/), 2025 data |
| 29 min | Average eCrime breakout time | same |
| +89% | Year-over-year activity by AI-enabled adversaries | same |
| 92% | Organizations with an AI-related breach that lacked proper AI access controls | IBM analysis of the 2026 Cost of a Data Breach Report |
| 43% | Organizations reporting incidents that involved unapproved AI | same; denominators differ |
| 19% | Organizations reporting real coordination between AI governance and security | same |

None of these measure any particular team's agents. They show how fast an attacker moves once a credential leaks.

**The control map**:

```
 agents              controls, enforced OUTSIDE the prompt            resources
 ──────              ─────────────────────────────────────           ─────────
 Test agent   ──►   Identity · Budget · Tool policy · Egress   ──►   Models
 Review agent ──►                                              ──►   MCP tools
 RCA agent    ──►                                              ──►   Network
                    every decision logged, the allowed AND the denied
```

**Where each control lives in a run**:

```
 BUILD                START               RUN                   RESPOND
 pin dependencies ──► scope identity ──►  restrict files    ──► stop the run
 scan secrets         set resource        and network           keep the evidence
                      limits              access
       └── tool/MCP interception checks each call · runtime policy limits files, creds, egress ──┘
```

**Containers, hardened images and microVMs protect different things**:

| Approach | Security boundary | Controls still needed |
|---|---|---|
| Container | Shared kernel, process isolation | Limit privileges, mounts, network and daemon access |
| Hardened image | Smaller software surface, same runtime boundary | Patch and pin images; runtime controls still apply |
| VM / microVM | Separate guest kernel, hypervisor boundary | Patch host and guest; scope files, secrets and egress |

**What the microVM boundary looks like** (from [Docker's Sandboxes architecture](https://docs.docker.com/ai/sandboxes/architecture/)):

```
 PER-SESSION microVM (own guest kernel)              HOST-SIDE CONTROLS (outside the guest)
 ┌──────────────────────────────────────┐            ┌──────────────────────────────────────┐
 │ agent ──► private Docker engine       │ ─────────► │ policy + credential proxy            │
 │ builds and test containers stay here │            │ (real API keys never enter the VM)   │
 │ no access to the host Docker socket  │ ─────────► │ MCP gateway                          │
 └──────────────────────────────────────┘            │ (host MCP servers need their own     │
            │                                         │  limits)                             │
            ▼                                         └──────────────────────────────────────┘
 workspace: prefer a PRIVATE CLONE over a direct host mount
```

Watch out with Docker Sandboxes: direct mounts write to the host, and deleting the VM doesn't undo those edits. Mounting the host Docker socket, or your whole home folder, into any container is effectively root on the laptop or runner.

**Agentic Drift: keep hold of intent** (Colleen Lake):

```
 INTENT ─────────► ISOLATE ─────────► VALIDATE ─────────► INTERVENE
 agree outcome,    branch/worktree,   CI, telemetry,      review exceptions,
 constraints,      keep it            user feedback       keep required gates
 stop conditions   reversible
      ▲                                                        │
      └──────────── evidence contradicts the plan? replan ─────┘
```

**Try it:** for each place an agent runs (laptop, CI runner, gateway, sandbox), can you show one allowed operation and one denied operation, each with a record you can attribute? It's a cheap verification exercise, and the gaps it finds are the ones that matter.

**Watch/read:** [Agentic Drift](https://www.wearedevelopers.com/events/world-congress-2026-north-america/sessions/1739-agentic-drift) · [The New Security Stack](https://www.wearedevelopers.com/videos/100607-the-new-security-stack) (may need a WeAreDevelopers account) · [CoreWeave on-demand library](https://coreweave.com/fully-connected-2026/on-demand) (lists "Securing AI at Scale: CoreWeave and CrowdStrike").

---

## 3. LillyPod: make AI fit the scientist

Eli Lilly, CoreWeave Fully Connected

**Why it matters:** the scale got the headlines, but the part worth copying is how the platform is organized around the people using it.

| Number | What | Source |
|---|---|---|
| 1,016 | NVIDIA Blackwell Ultra GPUs | [NVIDIA](https://blogs.nvidia.com/blog/lilly-ai-factory-live/) |
| 9,000+ | Reported petaflops of AI performance | same |
| 4 months | To assemble the system | same |
| ~90% / ~10% | Research vs enterprise usage | Conference observation |
| 8 nodes | Dedicated to agentic coding | same |


```
 ┌─────────────────────────────────────────────────────┐
 │ EXPERIENCE  familiar research tools and desktops    │ ◄── scientists work here
 ├─────────────────────────────────────────────────────┤
 │ MODELS      governed access + registry; the         │
 │             platform routes, users don't pick       │
 ├─────────────────────────────────────────────────────┤
 │ COMPUTE     scheduled accelerator capacity          │
 ├─────────────────────────────────────────────────────┤
 │ DATA        shared high-performance storage         │
 └─────────────────────────────────────────────────────┘
   + a "lab notebook" (W&B) for every run: inputs, model version, outputs
   + keep the HPC experts; learn from the research power users
```

Routing and governance were still evolving, so this isn't a finished reference architecture.

**Try it:** can someone go from a ticket or PR to the evidence behind an agent's result without stitching together three different histories? You can borrow the operating model without buying the hardware.

---

## 4. HumanLayer (Dex Horthy): the verification bottleneck

AGNTCon Day 1 · [Talk recording, "Fighting Code Slop"](https://www.youtube.com/watch?v=ix1qQK1IvmA) (posted by the Agentic AI Foundation under a different title from the program) · [Related AI Engineer talk](https://www.youtube.com/watch?v=Ib5GBkD555M) · [Write-up: Why Software Factories Fail](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md) · Horthy's articles 1–3: [the bottleneck](https://x.com/dexhorthy/status/2080697380379427275), [four reviews](https://x.com/dexhorthy/status/2081058573556306030), [the next change](https://x.com/dexhorthy/status/2081797628552270027) · SlopCodeBench runs: [Opus 5](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md), [Sol/Fable/Kimi](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-sol-fable-kimi-on-slop-code-bench.md) · [Session](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1291877)

**Why it matters:** a factory runs at the speed of its slowest box. Agents sped up *building*, not *reviewing*.


```
 vision ─► tracker ─► BUILD ─► tests ─► PR ─► CI ─► HUMAN REVIEW ─► prod ─► users ─► feedback ─┐
   ▲                   │                                │                                      │
   │          was: hours–days                    still: hours–days   ◄── the bottleneck moved  │
   │          now: minutes–hours (agent)                                                       │
   └───────────────────────────────────────────────────────────────────────────────────────────┘
 "Lights-off" factory = delete the HUMAN REVIEW box. HumanLayer tried it (July 2025). It didn't hold.
```

**The core idea: maintainability has no fast oracle.** A test tells you in seconds whether code *works*. Whether it's *easy to change* only shows up weeks later, when someone gets paged at 3 a.m. That delay is too long to use as a training reward, so models learn "tests pass" and nothing more: *"there is no penalty for eroding codebase maintainability"* (write-up). Until something can check maintainability quickly, **read the code**.

**The evidence:**

| Evidence | What it shows | Source |
|---|---|---|
| SlopCodeBench: the best model at launch scored **14.8%**; newer models only 1–1.5 points higher | Tests passing ≠ maintainable when requirements keep arriving | Talk |
| Faros AI: **31.3%** of PRs merged with no review, incidents per PR **+242.7%**, bugs per developer **+54%** | Quality signals slipped after teams adopted agents. The author calls it correlation, not proof | Write-up |
| Models got much better at one-off problems, barely better at improving a codebase | Better models aren't fixing this on their own | Write-up chart |

**Four reviews before a large diff** (the "missing middle" is program design):

```
 PRODUCT ────────► ARCHITECTURE ────► PROGRAM DESIGN ────► VERTICAL SLICE
 user pain,        service             types, signatures,    one working path,
 success signal    boundaries,         call/file changes     try it, review it
                   data contracts      ▲
                                       └── "the missing middle": architecture alone leaves
                                           many code decisions for the agent to improvise
 Scale it to the risk. A small, clear fix doesn't need four documents.
```

The write-up's own number: about **1 hour** of planning up front cut review from **~6 hours to ~20 minutes**. In its words, *"30 minutes of planning saves hours of review."*

**Slice vertically, not by layer:**

```
 HORIZONTAL (how models plan by default)      VERTICAL (what to ask for)
 ═══════════════════════════════════════      ══════════════════════════
 1. all DB changes                             1. one feature: DB → API → UI, working
 2. all API changes                            2. next feature: DB → API → UI, working
 3. all UI changes                             3. ...
 nothing works until step 3                    each step can be run, tested, redirected
```

**What happens on the next change?**. Horthy's small SlopCodeBench run added requirements to the same codebase over 8 checkpoints. Complexity rose for all three models plotted. Treat these as signals, not a full measure of maintainability.

![SlopCodeBench circuit_eval, checkpoints 1–8: mean cyclomatic complexity (left) and duplicated lines as % of source (right) for Opus 4.8, Sonnet 5 and Opus 5. From Horthy's article 3.](images/humanlayer-complexity.jpg)

What the figure shows, read from its own labels:

| Model | Mean cyclomatic complexity, ck1 → ck8 | Duplicated lines, ck1 → ck8 |
|---|---|---|
| Opus 4.8 | ~4.9 → ~8.3 ("goes up 70%") | ~4.5% → ~17% ("nearly quadruples") |
| Sonnet 5 | ~3.8 → ~4.7 | peaks ~20% at ck4–5, ends ~11% |
| Opus 5 | ~2.4 → ~2.6 | ~11.5% → ~9% |

Horthy also ran a TypeScript slop linter over the agents' code: **174.88 and 178.88** findings per 1,000 lines, against **15.06** in HumanLayer's own monorepo, about **11.6–11.9×**. That baseline is not human-written code. It is their *"99%-AI-generated-but-also-carefully-reviewed"* repo, so the gap is careful review, not human vs AI ([benchmark write-up](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md)). He built the 76-rule TypeScript detector set himself and flags that its parity with SlopCodeBench's Python rules is unverified. Both are small runs.

**His practices, and what they could look like day to day:**

| Practice | What he said | What it could look like |
|---|---|---|
| Plan before you build | Expected pain = P(you'll have to change it) × how painful the change is. Skip cheap decisions | Design docs scaled to the risk of the change |
| Align visually | [show-me](https://www.humanlayer.com/blog/show-me-skill): no "walls of agentic paragraphs" | Diagrams and tables in plans, not prose |
| Give agents back pressure | "Give them a browser. Let them run the app. Let them use curl." | Browser automation, local test runs, linters the agent can call |
| Feed user feedback in | A 3 a.m. page should "come with the PR the agent thinks will fix it" | Route alerts into a bug-fix agent that opens a draft PR |
| A loop = forward + back pressure | A trigger with no feedback is a slop generator on a timer | Schedule agents only alongside a feedback signal (tests, hooks, review) |
| Compound | "Analyze the sessions of your team" | Mine past agent sessions for repeated mistakes |

**His target:** work within the model's limits and aim for **2–3× faster with the quality kept**, not 10–100× faster.

**Try it:** for the next sizeable agent-built change, can the reviewer approve the shapes (contracts, types, file plan) and a thin slice *before* the agent builds the rest? Then add one realistic follow-up requirement and see whether the change fits the design or needs copied logic.

---

## 5. Michael Larson: ship skills like software

AGNTCon Day 2 · [Session](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1256939) · [Original slides (PDF)](https://sessionize.com/download/iglaflez~WVwsaBMFSGUwjtjhQq4vPK.pdf~shipping_agent_skills_safely1.pdf) · [TDD harness](https://github.com/mrlarson2007/copilot-tdd-harness)

**Why it matters:** skills spread like helpful notes, but they behave like code. skills.sh showed **3.9M** installs of `find-skills` (15 Oct snapshot). Larson named three problems:

| Problem | What it looks like |
|---|---|
| "It worked once" | It passed once, by luck, and nobody re-ran it |
| Malicious attacks | Malware disguised as setup steps; encrypted archives that slip past content scans |
| Cost | Every untested revision is paid for in tokens and in review time |

His fix: **treat skills like software.**

```
 VERSION ──────► EVALUATE ──────► REVIEW ──────► RELEASE
 track changes   paired evals     scan + human   distribute like a package
                 in CI            review         (APM, skills.sh / skills CLI)
```

**Setting up evals** (his recipe):

| # | Step | Why |
|---|---|---|
| 1 | Collect 5–10 tasks plus known failure modes | Small enough to re-run cheaply |
| 2 | Write deterministic assertions | Pass/fail with no judge involved |
| 3 | Compare the current and proposed skill in CI | Shows whether v2 is *better*, not just whether it runs |
| 4 | Re-run when the model changes | The model can improve without the skill, which can turn the skill into dead weight |
| 5 | Add adversarial cases | Skills carry attacks too |

**A paired eval**:

```
 fixture repo (seeded: off-by-one + missing null check)
        ├──► skill v1 (current)  ──┐
        │                          ├──► finds known defects? · avoids invented ones? · leaves files intact?
        └──► skill v2 (proposed) ──┘
        repeat on every skill change, model change and agent-client change
```

**The TDD harness: evidence is part of the contract**:

```
 ┌───────────────────────┐   delegates ONE cycle   ┌──────────────────────────────┐
 │ tdd (planner)         │ ──────────────────────► │ tdd-cycle-runner             │
 │ picks one behavior    │ ◄────────────────────── │ own context; returns a JSON  │
 └───────────────────────┘    JSON contract back   │ contract: code, tests, diff, │
                                                   │ commit evidence              │
                                                   └──────────────────────────────┘
 Promptfoo runs each case in a DISPOSABLE fixture repo · Jev grades the evidence from each phase
```

**Jev's real numbers** from one recorded RED-phase call (Larson's slide 12):

| RED judgment | Jev result |
|---|---|
| Focused test | 1.95 / 2 |
| Intended failure | 0.96 P(yes) |
| Scope preserved | 0.96 P(yes) |
| No RED commit | 0.91 P(yes) |

The call took 222 ms. Total Jev spend across all his runs: **$0.01**. One slide line matters a lot: **"Promptfoo records scores. CI checks completion. No pass thresholds."** Making a score *block* a release would be an extension, not his demo. The demo's "commit your changes" check is specific to that task, not a general rule.

**Two more slides worth repeating:** portability needs testing (a skill that assumes a tool named `Bash` can break on another agent with a different shell or approval model), and checking skills for attacks takes three steps: **scan → review → sandbox**.

**His challenge to the room:** *add an eval to one skill you're sharing.*

**Try it:** pick one high-traffic skill, freeze 5–10 fixtures from real misses plus one adversarial case, and re-run them on every skill, model or client change. When a case fails, check the fixture and the harness before blaming the model.

---

## 6. Block (Joah Gerstenberg): Cut the Noise

AGNTCon Day 1 · [Slides with sources](https://joahg.dev/cut-the-noise/) · [Slide PDF](https://sessionize.com/download/ibtatyec~fYYKmmxxU1W8LHdNvnjTZJ.pdf~cut-the-noise-joah-gerstenberg-agntcon-2026-1.pdf) · [block/review](https://github.com/block/review) · [Session](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1247706)

**Why it matters:** if there's too much code for people to read all of it, an automated reviewer has to be one people *listen to*. Block's first reviewer was noisy enough that coworkers deleted its comments, so Block rebuilt it. Slide title: **"A reviewer that's muted catches nothing."**


```
 OLD FACTORY                                   NEW FACTORY
 ═══════════                                   ═══════════
 writing ≈ reviewing (balanced, slow)          agents flood review inboxes
 engineers learn from each other               typical Block reviewer: ~3× the lines of a year ago
 through review                                review shrinks into a "ritual of trust"
                     "Review became the new rate limit."
```

**Anchor every finding to the customer.** The code was never the goal; the experience is. Could this change **double-charge** someone? A finding needs a trigger, a code path and a consequence.

**Four measurements, because any one of them alone can be gamed:**

| Layer | Metric | Question | Gamed alone by |
|---|---|---|---|
| Offline | Precision | Of what it flagged, how much was real? | Saying almost nothing |
| Offline | Recall | Of the known defects, how many did it find? | Flagging everything |
| Online | Address rate | Do engineers act on it? | Only making easy, agreeable findings |
| Online | Post-merge fix rate | Did acting on its advice cause harm? | (This one checks the other three) |

**The priority call: precision over recall.** *"A useful reviewer stays quiet when it has nothing worth saying."* As false positives fell, Block's address rate went back up.

**The architecture: more reviewers for recall, more layers for precision**:

```
 ┌───────────────────────┐
 │ Behavior & contracts  │──┐
 ├───────────────────────┤  │ candidates  ┌──────────────────────────┐  kept   ┌──────────┐
 │ Reliability & ops     │──┼───────────► │ COORDINATOR              │───────► │ PR       │
 ├───────────────────────┤  │             │ merges duplicates, tries │         │ comments │
 │ Security & trust      │──┘             │ to DISPROVE each one     │         └──────────┘
 └───────────────────────┘                └────────────┬─────────────┘              ▲
  each lens reads the WHOLE change          dropped    ▼                            │
                                          ┌──────────────────────────┐   restored   │
                                          │ JUDGE (different model)  │──────────────┘
                                          │ re-checks the DROPS      │
                                          └──────────────────────────┘
 Delivered by default: P0–P2 findings at confidence ≥ 0.8 (block/review README)
```

**Results on ReviewBench** (grounded = matches a labelled known issue):

| Metric | block/review |
|---|---|
| Grounded precision | **88.7%** |
| Grounded recall | **32.6%** |
| High-severity recall (separate subset) | 50% |
| For comparison: Copilot grounded recall at ReviewBench launch | 26% |

**Combine reviewers instead of crowning one.** Block's reviewer and another reviewer overlapped on only **22%** of findings. Each model and lens has different blind spots.

**Route human attention by risk.** He cites Meta's RADAR: *"A new test and a ledgering-contract change should not require the same treatment."* At Block, people still read the code for:

```
 infrastructure · public claims · SOX compliance · money movement · PII
```

Past review comments make good **measuring sticks** (labels to grade the reviewer against). They're poor **ingredients**: a comment records a conclusion, not the reasoning behind it, and feeding comments back in is what made Block's first reviewer noisier.

**What the job becomes:** align and contain → get review *before* the code exists (Buzz, CoPlan: shared planning sessions) → bring coworkers in while the approach is still forming.

**Compared with the PR reviewer I run:**

| Cut the Noise | My reviewer (Oct 2026) | Smallest step |
|---|---|---|
| Coordinator must disprove each finding with evidence | Evidence checks exist ✔ | Log every dropped finding with its reason |
| Three lenses + a judge on a different model | Single pass ✗ | Add one second lens; measure overlap |
| Precision bar before posting | I approve each post | Count the drafts I delete: that's a precision measure |
| Address rate, post-merge fix rate | Not measured ✗ | Count which posted findings authors acted on |
| Risk routing | Same depth for every PR | Tag PRs touching auth, database migrations or customer data for a deeper pass |

---

## 7. Drew Breunig: how contexts fail, and how to fix them

AGNTCon Day 2 · **[Talk write-up: The State of Context Engineering](https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html)** (24 Oct, ~40 slides) · [Context Inertia](https://www.dbreunig.com/2026/10/14/context-inertia.html) · Background: [How Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html), [How to Fix Your Context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html) · [Session](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1257835)

**Why it matters:** in 2024 the pitch was that million-token windows solve everything ("RAG is dead"). In practice, *long contexts fit more information **and more errors***, and agents run in exactly those conditions: many tools, many turns, long runs.

**Four ways context goes wrong**:

| Failure | What goes wrong | Talk example | What to watch for in your agents |
|---|---|---|---|
| Poisoning | A false fact keeps being reused | Gemini chased **tea** (FireRed) in a game that needs **lemonade** (Red) | An unverified RCA guess becomes "known" in the journal |
| Distraction | History crowds out fresh reasoning | Past ~100K tokens Gemini repeated old actions instead of planning | The same failed diagnostic, rerun |
| Confusion | Irrelevant context drives the choice | A small model failed with 46 tools and succeeded with 19 | Too many skills hide the right one |
| Clash | Instructions or facts disagree | Contradictory examples override the instruction (below) | Old environment rules sitting beside new ones |

**Chat history can override instructions** (Camassa & Shiller, [*Do as I Say, Not as I Do*](https://arxiv.org/abs/2605.20382)):

```
 system:   "Answer in Russian."
 history:  turn 1 (French) · turn 2 (French) · … · turn N (French)   ◄── hardcoded, contradicting
 question: about a violin
 measure:  does the reply still follow "Russian"?

 contradictory turns  N = 1 ─────────────────────────────► 50
 Claude Opus 4.6           0.98 ───────────────────────────► 0.13
 Gemma 3 12B               below half after only a few turns       (13 models tested)
```

![Camassa & Shiller: instruction-following rate (1.0 = always follows the instruction) for 13 models as contradictory turns N go from 1 to 50. Task-based panel.](images/context-heatmap.jpg)

A few rows read straight off the heatmap (the paper's columns are 1, 2, 3, 4, 6, 8, 11, 16, 22, 31, 43, 50):

| Model | N = 1 | 4 | 8 | 16 | 31 | 50 | Pattern |
|---|---|---|---|---|---|---|---|
| Claude 4.6 Opus | 0.98 | 0.98 | 0.91 | 0.69 | 0.38 | 0.13 | Holds until ~8, then slides |
| Claude 4.6 Sonnet | 0.90 | 0.95 | 0.74 | 0.51 | 0.29 | 0.15 | Same shape, earlier |
| GPT-5.2 | 0.66 | 0.60 | 0.59 | 0.58 | 0.50 | 0.48 | Never great, never collapses |
| Gemma-3 12B | 0.98 | 0.43 | 0.26 | 0.16 | 0.08 | 0.01 | Below half by N = 3 |
| Hermes-4 70B | 0.39 | 0.02 | 0.01 | 0.00 | 0.00 | 0.01 | 0.06 at N = 2 |

The takeaway is the *direction*: every model drifts toward the history once there's enough of it. "Stop doing X" typed into a long session competes with every turn that did X.

This is a controlled experiment, not a universal limit on chat length. It shows that repeated examples can outweigh an explicit instruction. Drew's write-up files it under *distraction*; I'd have put it under *clash*.

**The Pokémon harness mattered**:

```
 game RAM ──► harness extracts structured state ──► Gemini 2.5 ──► navigation + puzzle tools
              (Gemini struggled with pixel text)          │
                                                          ▼
                                     scratchpad memory ── wrong "find tea" goal survived summarization
 Result: playing from structured state was "roughly as good as" playing with vision
```

![The Gemini 2.5 Pokémon harness: game RAM → structured state → Gemini, with navigation and puzzle tools and a scratchpad memory.](images/pokemon-harness.jpg)

A concise memory is still wrong if the fact inside it is wrong. **Check facts before saving them as context.** Sources: [Drew's Pokémon case study](https://www.dbreunig.com/2025/06/17/an-agentic-case-study-playing-pok%C3%A9mon-with-gemini.html) · [Gemini 2.5 technical report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf).

**Six tactics, three jobs**:

```
 SELECT                       SEPARATE                       REFRESH
 augmentation (RAG, skills)   quarantine (fresh subagent)    pruning (drop irrelevant)
 tool loadout                 offloading (files, DB)         summarization (compaction)
```

**Tool loadout, as demoed** (DSPy):

```
 request ──► small model (Jev) scores every tool: "will the agent call it?"
                 │ keeps top k = 8 (a demo setting, not a rule)
                 ▼
             larger model runs the agent with ONLY those tools
 Selecting a tool ≠ authorizing it. Keep a governed way to add a tool that got filtered out.
```

His enterprise example loaded **~600 skills per engineer**. My own setup puts ~160 skill descriptions into every session: the same problem at a smaller scale.

**The arc:**

```
 prompt engineering (2023) ──► context engineering (2025) ──► harness engineering (2026)
   words for one call            assemble context dynamically    move that work into code
                 "LLM output is the product of context & weights"
```

**Persistent agents have a persistence problem**. METR time horizons: GPT-5 **3.4 h**, Gemini 3.1 **6.4 h**, Opus 4.6 **12.0 h**. Longer runs bring new failures:

| Problem | What happens | Example |
|---|---|---|
| Fighting the weights | Asking for something the model was trained against | Claude Code's system prompt repeats its parallel-tool instructions (7×, 4×, 2×, 3×) |
| Context inertia | Fixates on one hypothesis and won't back off | A Qwen agent spent hours on package versions; the real issue was an incompatible API endpoint |
| Forgetting helps | Dropping context beats keeping it | Memento ran until a fixed timeout (1.5 h in one experiment), wrote a short note, then restarted fresh; Fork-and-Flush and Tan et al. below |
| Dawdling | A long-running agent stops doing work but keeps talking | A CORAL agent found its last improvement at 231M tokens; of its final 1,500 turns, 98% made no tool call (Drew's [Context Inertia](https://www.dbreunig.com/2026/10/14/context-inertia.html)) |

**AHC014 (AtCoder Heuristic Contest), best mean score** (*Fork-and-Flush*, Cai & Ziakas, as presented in Drew's talk; v2 wrongly credited these to the Tan paper):

| Setup | Score |
|---|---|
| Team of 4 **with forgetting** | **1,144,695** |
| 4 parallel agents | 1,007,073 |
| 1 agent | 961,136 |

This is a task score on one contest problem, not general accuracy. It doesn't establish a universal reset interval.

**The slide-17 figure is a different paper** (Tan et al., [*Scaling Discovery Requires Forgetting*](https://arxiv.org/abs/2610.20563)), on the same contest:

![Tan et al.: AHC014 score vs total dollars spent for 1 agent, 4 parallel agents and a team of 4. After the first 30 proposals per agent, "Forget" (blue) restarts from the best work and "Continue" (grey) keeps the history.](images/context-forgetting.jpg)

```
 first 30 proposals ──┬──► CONTINUE: keep the whole history   → < 2% more over the next 30
                      └──► FORGET:   keep the best artifact,  → 4.5–9.2% more over the next 30
                                     drop the conversation
 In all three setups the blue (Forget) line peaks higher than the grey (Continue) line.
```

The paper's abstract reports up to 15% over parallel agents and up to 39% over a single agent. Each panel has its own score scale (roughly 0.8M–1.1M), so read the gap, not the absolute numbers.

**"Our solutions move the problem":**

| Fix | The problem it creates |
|---|---|
| Longer context windows | Let in more bad information |
| Agents that run for a long time | Run past the point of usefulness and ignore your preferences |
| Moving state into the harness | 2027 prediction: memories and skills pile up and conflict, so *strategic forgetting* will matter |

**Worked example: recovering a stuck RCA agent**

```
 COMPACT THE SAME HISTORY                     CHECKED HANDOFF → FRESH CONTEXT
 ════════════════════════                     ════════════════════════════════
 "package-version mismatch" (wrong)           goal:       explain the failing build
   └─ summarized neatly                       evidence:   these revisions + log links
        └─ still "package-version mismatch"   rejected:   package-version (failed check X)
                                              side effects done: none, no files changed
 a neater summary of a wrong idea is          constraints + approvals: still in force
 still a wrong idea                           next test:  does the failing config differ
                                                          from the passing one?
```

Keep completed side effects and approval boundaries in the handoff. Losing either can cause duplicate work or change what the agent is allowed to do.

**Try it:** compare your current context handling against task-specific loadout plus a checked handoff, on the same tasks. Measure completion, wrong tool choices, repeated failed actions, tokens and time, and count the cases where filtering hid a necessary tool. Using fewer tokens alone doesn't count as success.

His closing line: *the job is choosing where to be deterministic and where to be probabilistic.*

---

## 8. Also worth knowing (other talks)

| Talk | The one idea | Why it matters |
|---|---|---|
| MCP keynote and others | MCP in 2026: stateless ([SEP-1442](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1442), shipped via SEP-2575 in May 2026, so a gateway can authorize each call), **elicitation** (server asks the user), **Tasks** (long work, check back later), Skills and Apps, **tool search ~20K → <1K tokens**, WebMCP | Tool search is tool loadout built into the protocol |
| Harbor | Diagnose **task → harness → model**. ~⅓ of the hardest benchmark tasks were broken, not hard. Model effect is 5.2× the harness effect, but timeouts follow the harness. An LLM judge was trusted only at κ ≥ 0.5 agreement with humans (humans agreed with each other at 0.66; the judge with humans at 0.51). From 6,000+ trajectories they built **12 failure modes in 3 groups** (below) | When an eval fails, check the fixture first |
| [Yuki Watanabe](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1259081) · [Prathmesh Patel](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1258153) | Regression suite: capture a failing trace and turn it into a scored case ("feedback are the new tests"). CI/CD gates: a tool description is code; deterministic checks hard-fail, evals only score | The "learn" step in the reading map |
| [Adaptive Security](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1238862) | Once people trusted the bot, *"the judges went quiet."* A Gmail connector gained a send tool and Claude started emailing clients | Evals are an operation, not a project; review connector changes like dependencies |
| Adrian Warman (Orkes) | *"Let agents solve the problems they solve best, let workflows orchestrate and provide the deterministic layer."* | Chain RCA → bug fix → PR review in one workflow |
| [Nnenna Ndukwe (PolicyNIM)](https://events.linuxfoundation.org/agntcon-mcpcon-north-america/program/schedule/?id=1201093) | Pull in the relevant policies, with citations, *before* code is written; refuse to proceed when the evidence is weak | The "before" half of review, paired with Block's "after" |
| goose ([Douwe Osinga](https://github.com/block/goose), Block): *Agentic State Machines* | *"The conversation becomes the state."* Each behavior (compaction, subagents, approval) is an operation that returns durable effects, not another `if` in the loop | The "resume without repeating a side effect" part of experiment 3 |
| Hydro | Enforce universal properties with types and frameworks: *"guardrails that sit outside the agent"* | A fast oracle for a narrow set of properties |
| Entire | Teams with coding agents ship 5× the PRs, each 3× larger; prompts kept with every commit | Sessions and plans are becoming part of the codebase |
| "Evals are the new PRDs" | Write the AI tests first (credited to Dianne Penn, Anthropic) | Matches Larson's paired evals |

**Harbor's failure taxonomy** (Han Xu, *Why Your Agent Is Failing*; 6,028 failed hard-task runs). Useful as the label set for experiment 1's failures:

```
 CAPABILITY                    OPERATIONAL                     PROCESS
 model didn't know             never reached the grader        how it ran, judged itself
 ──────────────────────────    ────────────────────────────    ────────────────────────────
 wrong factual answer  25.5%   silent deliverable ("Done ✓",   step budget / timeout
 algorithmic bug       18.7%     no file written)              false success claim
 hidden-test regress.   8.2%   environment block (403, pip)      (passed its own smoke test)
 wrong target / layer          syntax / language error         plan over implementation
                               wrong output schema               (never wrote the file)
 low-κ rubrics together: ~19%

 diagnose in this order:  TASK (is the fixture broken?) ──► HARNESS ──► MODEL (swap last)
```

---

## 9. Three experiments worth running

Three small experiments I'd run next, sized so any team can try them in a sprint or two.

```
 NeMo + Larson + Harbor ──────────► 1 ONE SKILL EVAL
 Block + Adaptive ────────────────► 2 ONE TRUSTED REVIEW
 Drew + Security + LillyPod ──────► 3 ONE CONTROLLED RUN
 HumanLayer ──────────────────────► "next change" case inside 1 and 3
```

| # | Experiment | What to do | Done when |
|---|---|---|---|
| 1 | **One skill eval** | Pick one high-traffic skill. Freeze 5–10 fixtures from real misses, plus one adversarial case and one follow-up-requirement case. Run v1 vs v2 with deterministic assertions; re-run on model change | Reusable fixture set + a one-page result; failures traced to fixture, harness or model |
| 2 | **One trusted review** | Score your PR reviewer on ~20 labelled PRs: precision, recall, agreement (κ) with human labels. Log each dropped finding with its reason; trial one second lens; tag high-risk PRs for a deeper pass | Baseline precision/recall + an address rate you can track |
| 3 | **One controlled run** | RCA → fix → PR review with one shared run ID. Task-specific loadout; checked handoff on repeated failure; one allowed + one denied action per runner; resume without repeating a side effect | Evidence linked end to end; a list of the controls that exist and the ones still to build |

**Each experiment has a cheaper alternative. Here's why I'd pick the recommended path:**

| # | Recommended (A) | Alternative (B) | Why A |
|---|---|---|---|
| 1 | Deterministic checks first (did it read the log, cite the failed job, avoid inventing an owner?), then a judge only for clarity | One LLM judge reading the final answer, as in my NeMo pilot (§1) | B scored 0.83–0.88 without seeing any evidence. A fluent wrong answer passes B |
| 1 | Planner hands one TDD cycle at a time to a fresh subagent that returns JSON (Larson's harness) | One long session with "remember to write the failing test first" reminders | Failed output piles up in a long session, and §7 shows history beating instructions |
| 2 | Specialists → skeptic coordinator → judge on the drops (Block) | One prompt with a higher confidence bar | B buys precision by dropping the subtle, high-severity findings |
| 2 | Full review when a PR goes Draft → Ready (or on a label); cheap deterministic checks on every push | Full multi-pass review on every push | Five model passes per commit adds latency and cost where nobody is reading yet |
| 3 | Reset rule: after 3 failed repair attempts on the same assertion, save the diff, end the session, start fresh from a checked handoff | Keep compacting the same conversation | Compaction keeps the wrong hypothesis (§7, AHC014 and Memento). The threshold of 3 is ours to tune, not from a talk |

---

## 10. Tools worth investigating

These are candidates, not adoption decisions. Start from the experiment and the missing capability, then pick the smallest tool that fills it.

### Testing and code quality

| Tool | Useful for | Talk |
|---|---|---|
| [Promptfoo](https://www.promptfoo.dev/docs/intro/) | Paired skill tests in CI | Larson |
| [Larson's TDD harness](https://github.com/mrlarson2007/copilot-tdd-harness) | A phase-and-evidence contract | Larson |
| [block/review](https://github.com/block/review) | Specialists + skeptical filter + appeal | Block |
| [ReviewBench](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/) | Labelled PRs for scoring a reviewer | Block |
| [show-me](https://www.humanlayer.com/blog/show-me-skill) | Visual plans before a large diff | HumanLayer |
| [SlopCodeBench](https://github.com/SprocketLab/slop-code-bench) | Sequential requirements on the same code | HumanLayer |
| [Harbor](https://github.com/harbor-framework/harbor) | Separate task env, agent run and checks | Harbor |
| [NeMo Agent Toolkit](https://docs.nvidia.com/nemo/agent-toolkit/latest/index.html) | Historical pilot only | Deprecated Oct 2026 |

### Runtime, context and evidence

| Tool | Useful for | Talk |
|---|---|---|
| [agentgateway](https://agentgateway.dev/) | Policy around model and tool calls | Security |
| [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) | microVM file and network limits | Security |
| [LangSmith](https://docs.langchain.com/langsmith/evaluation-types) / W&B | Traces and evaluation | LillyPod |
| [DSPy + Jev](https://dspy.ai/current/tutorials/jev_decisions/) | Task-specific tool loadout | Drew |
| [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) / [MCP Tasks](https://modelcontextprotocol.io/extensions/tasks/overview) | Checkpoints / async task handles (neither alone is a durable workflow) | Workflow talks |
| [Entire](https://entire.com/blog/an-entirely-new-git-hosting-network) ([CLI](https://github.com/entireio/cli)) / [AgentsView](https://www.agentsview.io/) | Recover sessions and the reasons behind a commit | Conference tools |
| Buzz / [CoPlan](https://github.com/block/coplan) | Review plans together before implementation | Block |

### Also worth a look

| Tool | Useful for | Note |
|---|---|---|
| [Dash0](https://www.dash0.com/documentation) | OpenTelemetry logs, metrics and traces in one place | Could link an agent's change to its runtime behavior |
| [Arize Phoenix](https://arize.com/docs/phoenix/) | Open-source tracing and eval UI | Pairs with OpenTelemetry-based tracing |
| [LiteLLM](https://docs.litellm.ai/) | One proxy in front of many model providers | My NAT pilot reached a local Nemotron through it |
| [LlamaIndex](https://developers.llamaindex.ai/python/framework/) | Extraction that keeps page and table positions | A value read from the wrong column gives a confident, false answer |
| [Strands Agents](https://strandsagents.com/latest/) | Code-defined agents and multi-agent coordination | Alternative orchestration layer |

---

## 11. Papers and posts

| Read | Why | Test locally by |
|---|---|---|
| [The State of Context Engineering](https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html) | Drew's full talk | — |
| [Why Software Factories Fail](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md) | Horthy's full argument, ~35 figures | — |
| [SlopCodeBench](https://arxiv.org/abs/2603.24755) | Agents extending their own code over changing requirements | Adding a follow-up change to a passing task |
| [Do as I Say, Not as I Do](https://arxiv.org/abs/2605.20382) | Contradicting history vs instructions | Measuring adherence after N failed attempts in an RCA run |
| [Scaling Discovery Requires Forgetting](https://arxiv.org/abs/2610.20563) | Fresh contexts from retained work beat continuing | Checked handoff vs compaction |
| [LLMs Get Lost In Multi-Turn Conversation](https://arxiv.org/abs/2505.06120) | Failing to recover from early assumptions | Recovery tests |
| [RAG-MCP](https://arxiv.org/abs/2505.03275) | Retrieve tool descriptions before selection | Tool-choice accuracy and wrongly excluded tools |
| [Less is More](https://arxiv.org/abs/2411.15399) | Fewer functions → better selection (edge models) | Validating on your stack |
| [Provence](https://arxiv.org/abs/2501.16214) | Context pruning for RAG | Checking the supporting passage survives pruning |

---

## Questions I'm still working through

1. **One eval harness or two?** Skill evals (an `evals.json` next to the skill) and workflow evals (frozen ticket bundles, as in my NeMo pilot) could share one fixture format. Is one repo-local `evals/` folder simpler, or do they want to stay apart?
2. **When should the full review run?** Draft → Ready (or a label) seems like the right trigger for a multi-pass reviewer, with only deterministic checks on each push. Is that too late?
3. **Where's the reset line?** Agents that compact automatically can keep a wrong hypothesis alive (§7). I strongly think long runs need a no-progress reset. Is "3 failed attempts on the same assertion" about right, or is "N turns without a tool call" a better signal?

If you've tried any of these, I'd like to hear what worked.

---

## How to read the numbers

One caveat box in place of a disclaimer in every paragraph:

- **Speaker and vendor figures are attributed, not re-measured.** That covers NVIDIA, CrowdStrike, IBM, Block internal data, Faros AI and HumanLayer's runs.
- **Benchmarks don't transfer.** SlopCodeBench, ReviewBench and AHC014 results describe their own tasks and versions. Borrow the *method*, measure your own.
- **Small demos aren't performance evidence.** That includes my NeMo pilot (5 replies) and Larson's single Jev call.
- **The applications are proposals.** The "Try it" lines and §9 are my synthesis, kept separate from what the speakers said.
- **Source status:** original slides were found for Block, Larson and Drew (write-up). HumanLayer has a recording and a write-up. No standalone PolicyNIM or LillyPod deck was located. Video pages may need accounts.

**Sources:** my notes from all three conferences, and the original slides and posts linked in each section. Product status was checked 30 Oct 2026.