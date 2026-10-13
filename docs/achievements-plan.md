# Achievements — Planning Document

A working catalog copied from the tournament project. Code paths and account
planning references below refer to that separate application. The original system
was roadmapped in its `player-accounts-plan.md` §7 (Phase 2 — no player accounts/login
required, just the Phase 1 cross-tournament identity linking). Names here are placeholders —
fun/fitting naming is deliberately a later pass, same as artwork. The point of this document is
locking down *what* each achievement means and *how it's computed*, since that's the part that has
to be right before either of those.

Profile showcases, corporation XP, overall player levels, and cosmetic rewards are explored in
the separate [progression proposal](achievement-progression-plan.md). Its thresholds are draft
values; it does not replace this catalog's win-based achievement definitions.

The "How it's computed" column is internal only — never shown to the player, same spirit as the
rest of this app's data model (the achievement itself should feel like a fact about the game, not
a formula).

Four readiness tiers, called out per section:
- **Ready** — computable today from data already recorded, once the achievement engine itself
  exists (Phase 2).
- **Needs mapping** — needs a corporation → expansion table that doesn't exist yet (today's
  `src/lib/corporations.ts` is one flat list of 36 names, no Venus/Colonies/Turmoil tagging).
- **Needs corp list** — needs a corporation to be addable at all first (some Promo corporations
  below aren't in `src/lib/corporations.ts`'s picker yet), *then* the same expansion mapping as
  above. A strictly earlier blocker than "Needs mapping."
- **Needs history** — needs the Phase 1 cross-tournament identity linking itself (no accounts or
  login required for this, see `player-accounts-plan.md` §2), no new data fields.

---

## The Final table

A player can earn **Finalist** independently of placement — it's a participation fact, not
suppressed by or dependent on Champion/Silver/Bronze the way the round badges suppress each
other. Only three placement tiers exist here on purpose: the Final can run 3–5 players when a
genuine tie extends the field, so there's no standing "4th Place Finalist" / "5th Place Finalist"
achievement to define — Finalist already covers everyone who isn't podium.

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Finalist | Played at the Final table, any placement | A recorded match with `round === 99` includes this player | Ready |
| Champion | Won the Final | `position === 1` in the `round === 99` match | Ready |
| Silver Medalist | 2nd place in the Final | `position === 2` in the `round === 99` match | Ready |
| Bronze Medalist | 3rd place in the Final | `position === 3` in the `round === 99` match | Ready |
| Worth the Wait | Reached the Final only because a genuine tie for 4th extended the field | Reuses `determineFinalists`' own tie-extension logic — true for any finalist whose pre-Final standings rank was below 4th | Ready |
| Front Runner | Led the real standings after every single round, start to finish | Your `rank` is 1 when standings are recomputed after each round, not just at the end — distinct from Clean Sweep, since a tiebreak-driven lead doesn't require winning every round outright | Ready |

## Tournament Standing

*(final rank, or every-round consistency, in a tournament's real standings)*

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Finish Top Ten | Finished top 10 in a tournament's final standings | `rank <= 10` | Ready |
| Clean Sweep | Won every round in a tournament | `position === 1` on every recorded `roundPlacements` entry | Ready |
| Forever Second | 2nd in every round | `position === 2` on every round | Ready |
| Perpetual Bronze | 3rd in every round | `position === 3` on every round | Ready |
| Rebuilding Season | Last in every round | `position === table size` on every round — genuinely rough tournament required | Ready |

## Tied Games

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Won It on Tiebreaker | Your tournament rank was decided by TR margin or Opponent Strength rather than a clean TP lead | `tieKind(standing)` is non-null — this is the tournament-standings sense, not the in-game money-to-production tiebreak chain (that one isn't captured at all today, would need new fields; keeping to the standings sense since that data already exists app-wide) | Ready |
| Identical Twins | Still tied with another player on tournament points and both configured tiebreakers in the final standings | `tieKind(standing, steps) === 'complete'` — `completeTieWith` identifies a complete tie; equal TP and both configured tiebreaker values mean the players share a rank | Ready |
| Impossible | Still tied with another player on tournament points and all three metrics: TR margin, Buchholz, and TPerf | Compare TP and all three metric values directly. `tieKind === complete` covers only the configured pair, so it is insufficient by itself | Ready (explicit three-metric comparison needed) |
| Dead Heat | Recorded exactly the same TR as the player directly below you in a round | Compare adjacent players in recorded placement order; this player is not last and both `terraform_rating` values are equal. Use `trMarginFor === 0` only where it represents this same adjacent comparison | Ready |
| Tied Game Win | Shared first place in a recorded tied game (1st, 1st, 3rd, 4th) | Recorded placements are `[1, 1, 3, 4]`, and this player is one of the two players with `position === 1` | Ready |
| Tied Game Second | Shared second place in a recorded tied game (1st, 2nd, 2nd, 4th) | Recorded placements are `[1, 2, 2, 4]`, and this player is one of the two players with `position === 2` | Ready |
| Tied Game Third | Shared third place in a recorded tied game (1st, 2nd, 3rd, 3rd) | Recorded placements are `[1, 2, 3, 3]`, and this player is one of the two players with `position === 3` | Ready |

## Margins & peaks

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Nail-Biter | A whole table finished within 5 TR, top to bottom | Reuses the "closest whole table" spread calc already in `TournamentStats.tsx`: winner's TR minus last place's TR <= 5 | Ready |
| Mercy Rule | Won a game by 30+ TR over 2nd place | `trMarginFor` for the winner >= 30 — reads "win a game with 30 plus TR" as margin of victory, not raw TR, since raw TR >= 30 is true of nearly every winning game | Ready |
| Dominant Force | Finished a tournament with the single highest TR margin | Top row when the real standings are sorted by `trMargin` — literally what `/tiebreak-leaderboard?sort=trMargin` already shows | Ready |
| Gauntlet Runner | Finished a tournament with the single highest Opponent Strength | Same idea, sorted by `opponentStrength` | Ready |
| High Score | Recorded the single highest TR of any game in that tournament | Max `terraform_rating` across every match in the tournament, winner takes it regardless of placement | Ready |
| So Close | Finished 2nd, exactly 1 TR behind 1st | `trMarginFor` on a `position === 2` finish equals exactly -1 — the losing counterpart to Mercy Rule | Ready |
| Biggest Win | Your win was the biggest margin (1st vs. 2nd) of any game in the tournament | Directly reuses the "Biggest Win" highlight already computed in `TournamentStats.tsx` (`biggestWins`, the `closestGames`/`trMarginFor`-based calc) — the superlative counterpart to Mercy Rule's fixed +30 threshold | Ready |
| Photo Finish | Your table was the single closest table (top to bottom) of any in the tournament | Reuses the *table-spread* calc, not the 1st-vs-2nd one — the same `tableSpreads`/`closestTables` data Nail-Biter's fixed <=5 threshold already uses in `TournamentStats.tsx`, just taking the tournament's one minimum spread instead of checking against a cutoff. The superlative counterpart to Nail-Biter, the way Biggest Win is the superlative counterpart to Mercy Rule | Ready |
| Efficiency Expert | Finished a tournament with the single highest TPerf | Top row when the real standings are sorted by `terraformingPerformance` — literally what `/tiebreak-leaderboard?sort=terraformingPerformance` already shows. The TPerf counterpart to Dominant Force/Gauntlet Runner | Ready |
| Overachiever | Recorded a TPerf of 2.0+ in a single round | `tperfFor` for that round >= 2.0 — your table's output was double your fair share. The per-round counterpart to Efficiency Expert, same relationship Century Club has to Dominant Force | Ready |

## Milestones & awards

*(promoting the existing per-round badges to a lifetime achievement)*

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Milestone Collector | Claimed every milestone in a round, at least once ever | `roundAchievements().allMilestones` true at least once across history | Ready |
| Award Season | Won every award in a round, at least once ever | `roundAchievements().allAwards` true at least once | Ready |
| Shut Out | Won a round while claiming zero milestones and zero awards | `position === 1`, `milestones_claimed === 0`, `awards_won === 0` — proof a win can come from TR alone | Ready |
| The Full Package | Won a round while claiming every milestone and every award | `roundAchievements().perfect` true — the career promotion of the round-level "Perfect Round" badge, same relationship Milestone Collector/Award Season have to their own badges, and the opposite extreme from Shut Out | Ready |

## TR milestones

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Century Club | Recorded a 100+ TR game | `terraform_rating >= 100` on any match | Ready |
| Double Century | 200+ TR | `>= 200` | Ready |
| Triple Century | 300+ TR | `>= 300` (cricket scoring, since it already fit) | Ready |

## Corporation loyalty

Three tiers, escalating from a single tournament to a career:

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Creature of Habit | Played the same corporation in 2 rounds of one tournament | Group a tournament's matches by `corporation` for this player, any corp appearing >= 2 times | Ready |
| One Corp Wonder | Played the same corporation in every round of one tournament | Same grouping, one corp covers all qualifying rounds | Ready |
| Never the Same Twice | Played a different corporation in every round of one tournament | Same grouping, inverse condition — no repeats across the tournament's qualifying rounds | Ready |
| The Specialist | Won 3+ times with the exact same corporation, across tournament history | Group wins by corporation across every tournament, any count >= 3 — see also the per-corporation win-tier system below, which this effectively generalizes | Needs history |

## Flavor

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Beat the Fryx | Finished ahead of a player named Fryxelius in a game | Opponent's `player_name` matches `/fryx/i` and your `position` < theirs — a nod to the game's designer, computable today with zero new data, regardless of whether anyone's actually named that in a given tournament | Ready |
| Welcome to Mars | Finished last at a table at least once | Self-explanatory, universal enough that nearly everyone eventually earns it | Ready |
| Lucky Seat | Won 3+ games while seated as first player | `firstPlayerName` (seat 0 in `match.players`, same logic `MatchTable` already uses for the "first player" badge) equals you, and `position === 1`, on 3+ separate matches | Ready |
| From Behind | Won a game while seated last in turn order | The last seat in `match.players` (opposite the `firstPlayerName`/seat-0 "first player") equals you, and `position === 1` — the harder-seat counterpart to Lucky Seat | Ready |
| Underwater | Finished a game with TR below 50 | `terraform_rating < 50` — a notably weak final TR for a competitive game, well below typical winning totals | Ready |
| Full Field | Played in a tournament with 100+ entrants | Tournament's total player count >= 100 — `tournament-example` itself would already qualify | Ready |
| Spoiler | Beaten the player who went on to win *this* tournament, at some point in a qualifying round | Compare your `position` against the eventual champion's at any shared table, this tournament only — unlike Giant Slayer, this needs no cross-tournament history at all | Ready |
| Growth Mindset | Improved your own TR in every successive round of a tournament | This player's `terraform_rating` strictly increases from Round 1 → 2 → 3 | Ready |
| Jack of All Trades | Claimed at least one milestone *and* at least one award, in every round of a tournament | `milestones_claimed >= 1` and `awards_won >= 1` on every recorded round — the balanced counterpart to Shut Out | Ready |
| The Big Table | Won a 5-player game | `position === 1` where the match's table size is 5 — the rarer, harder table | Ready |

## Event day (manually awarded)

Nothing here is computable from match data — these describe something that happened at the venue,
not in a game. An organizer grants these directly (a quick action in the admin UI during the
event), inserting straight into `player_achievements` with no check logic at all. See the "Manual"
check type now noted in `player-accounts-plan.md` §7.

"Manually awarded" still needs a consistent bar, not just organizer whim — the Requirements column
is what the organizer actually checks before granting it, same role the "How it's computed" column
plays for the automatic ones.

| Name | Achievement | Requirements | Status |
|---|---|---|---|
| Retail Therapy | Bought something from the tournament store | Any recorded store purchase that day, any amount | Manual |
| Early Bird | First to check in on tournament day | Needs a check-in process with a timestamp or at least an ordered sign-in sheet — the literal first arrival | Manual |
| The Helper | Volunteered to help run the event | Organizer confirms the player did some unpaid task that day (registration desk, pairings, scorekeeping, etc.) | Manual |
| Costume Contest | Wore a themed Mars/sci-fi costume to the event | Visually confirmed by the organizer | Manual |
| The Raffle Winner | Won a door prize or raffle at the event | Needs the event to actually run a raffle — confirmed against that raffle's own recorded winner | Manual |
| Merch Mogul | Biggest spender at the tournament store on the day | Needs the store to actually track sales per person (even an informal tally) — the single largest total spend of the event, one winner | Manual |
| Dressed for the Part | Wore tournament merch to the event | Visually confirmed by the organizer at check-in or during the day | Manual |
| Globe Trotter | Traveled from outside the tournament's host country to attend | Could become computed instead of manual once a **Country** field on the profile and a host-country field on the tournament both exist (neither exists today); manual award works as a stopgap | Manual (future: computed) |

## Corporation

A per-corporation win-count ladder, seven tiers per corporation, same escalating-tier idea as TR
milestones (Century/Double/Triple Century) but applied per corporation instead of once overall:

| Tier | Wins required |
|---|---|
| Novice | 1 |
| Regular | 3 |
| Veteran | 5 |
| Expert | 10 |
| Master | 20 |
| Elite | 25 |
| Legend | 50 |

**Naming**: `{Corporation} {Tier}`, e.g. "Ecoline Novice," "Ecoline Legend".

**Suppression**: a leveling ladder, not seven permanently-visible badges — earning a higher tier
suppresses every lower tier of that same corporation on display, the same way Perfect/All
Milestones/All Awards suppress each other at the round level. Reaching 5 wins with Ecoline shows
"Ecoline Veteran" and hides "Ecoline Novice"/"Ecoline Regular," not all three at once. Every tier
still gets its own `player_achievements` row when earned (so "when did they first hit 5 wins"
stays answerable later), this only governs what's shown on the profile.

**How it's computed (shared template, same for every corp/tier pair)**: count of matches where
`corporation === '{Corporation}'` and `position === 1` for this player, across every tournament,
>= the tier's win count.

**Status**: every corp below needs cross-tournament history regardless of which box it's from
(counting wins with one named corporation doesn't need the expansion mapping at all — that's only
for "won with every corp in a box" achievements, which this per-corp system has effectively
replaced). The seven **Promo** corporations are blocked earlier than that: they aren't addable in
`src/lib/corporations.ts`'s picker at all yet, so they're listed here for documentation only.

The original "won every corp in a box" ideas this ladder replaced, kept here for completeness:

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Corporate Completionist | Won with every Base Game corporation at least once | Group wins by corporation across tournament history; all 12 Base Game names represented | Needs mapping |
| Venus Veteran | Won with every Venus-expansion corporation | Same grouping; all 5 Venus names represented | Needs mapping |
| Colonial Conqueror | Won with every Colonies corporation | Same grouping; all 5 Colonies names represented | Needs mapping |
| Agent of Chaos | Won with every Turmoil corporation | Same grouping; all 5 Turmoil names represented | Needs mapping |

| Corporation | Expansion | Status |
|---|---|---|
| Ecoline | Base Game | Needs history |
| Credicor | Base Game | Needs history |
| Helion | Base Game | Needs history |
| Interplanetary Cinematics | Base Game | Needs history |
| Inventrix | Base Game | Needs history |
| Mining Guild | Base Game | Needs history |
| Phobolog | Base Game | Needs history |
| Saturn Systems | Base Game | Needs history |
| Teractor | Base Game | Needs history |
| Tharsis Republic | Base Game | Needs history |
| Thorgate | Base Game | Needs history |
| United Nations Mars Initiative | Base Game | Needs history |
| Aphrodite | Venus | Needs history |
| Celestic | Venus | Needs history |
| Manutech | Venus | Needs history |
| Morning Star Inc. | Venus | Needs history |
| Viron | Venus | Needs history |
| Aridor | Colonies | Needs history |
| Arklight | Colonies | Needs history |
| Polyphemos | Colonies | Needs history |
| Poseidon | Colonies | Needs history |
| Stormcraft Incorporated | Colonies | Needs history |
| Cheung Shing Mars | Prelude 1 | Needs history |
| Point Luna | Prelude 1 | Needs history |
| Robinson Industries | Prelude 1 | Needs history |
| Valley Trust | Prelude 1 | Needs history |
| Vitor | Prelude 1 | Needs history |
| Ecotec | Prelude 2 | Needs history |
| Nirgal Enterprises | Prelude 2 | Needs history |
| Palladin Shipping | Prelude 2 | Needs history |
| Sagitta | Prelude 2 | Needs history |
| Spire | Prelude 2 | Needs history |
| Lakefront Resorts | Turmoil | Needs history |
| Pristar | Turmoil | Needs history |
| Septem Tribus | Turmoil | Needs history |
| Terralabs Research | Turmoil | Needs history |
| Utopia Invest | Turmoil | Needs history |
| Arcadian Communities | Promo, not yet selectable | Needs corp list |
| Astrodrill | Promo, not yet selectable | Needs corp list |
| Factorum | Promo, not yet selectable | Needs corp list |
| Kuiper Cooperative | Promo, not yet selectable | Needs corp list |
| Mons Insurance | Promo, not yet selectable | Needs corp list |
| Pharmacy Union | Promo, not yet selectable | Needs corp list |
| Philares | Promo, not yet selectable | Needs corp list |
| Recyclon | Promo, not yet selectable | Needs corp list |
| Splice | Promo, not yet selectable | Needs corp list |
| Tycho Magnetics | Promo, not yet selectable | Needs corp list |

## Milestone & Award Mastery

Two more leveling ladders, same shape and same seven tier names as the per-corporation win ladder
above, but counting lifetime *claims* instead of wins — a player who never wins a game, or never
settles on one corporation, can still visibly progress here.

| Tier | Milestones claimed (lifetime) | Awards won (lifetime) |
|---|---:|---:|
| Novice | 5 | 5 |
| Regular | 15 | 15 |
| Veteran | 30 | 30 |
| Expert | 60 | 60 |
| Master | 100 | 100 |
| Elite | 150 | 150 |
| Legend | 250 | 250 |

**Naming**: `Milestone Marathon {Tier}` and `Award Collector {Tier}` — two independent ladders, so a
player can sit at a different tier on each (e.g. "Milestone Marathon Veteran" while still
"Award Collector Regular").

**Suppression**: same leveling behavior as the Corporation ladder — only the current tier of each
ladder shows on the profile; lower tiers of that same ladder still get their own
`player_achievements` row, they just don't display once superseded.

**How it's computed**: sum of `milestones_claimed` (respectively `awards_won`) across every
recorded match for this player, across every tournament, compared against the tier threshold.

**Status**: Needs cross-tournament history — same constraint as the per-corporation ladder above
and everything under the next heading.

## Cross-Tournament

Artwork is available in the Cross-Tournament gallery. The current checklist labels these
**Needs accounts**; evaluation needs stable player identities linked across tournament history.
This studio previews the concepts and does not evaluate or award them.

The Phase 1 identity-linking work itself — no new fields, just needs a player linked across
tournaments (no account/login required for this, see `player-accounts-plan.md` §2).

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Giant Slayer | Beaten a player who has won a championship in some tournament | At query time, check whether that opponent has ever had `position === 1` in any tournament's `round === 99` match | Needs history |
| Regular | Played in 2 tournaments | Count of distinct tournaments this player appears in >= 2 | Needs history |
| Veteran | Played in 3 tournaments | Same count >= 3 | Needs history |
| No Rest for the Weary | Played in 5+ tournaments | Same count >= 5 | Needs history |
| Hat Trick | Won 3 tournaments, lifetime | Count of tournaments where this player's final `rank === 1`, >= 3 | Needs history |
| The Specialist | *(see Corporation loyalty above)* | | Needs history |
| Corporation Collector | Played 20+ unique corporations across tournament history | Distinct `corporation` values across every recorded match for this player, count >= 20; no fixed total-corporation denominator | Needs history |
| On the Rise | Finished a tournament ranked higher than your previous one | Compare `rank` in this tournament's final standings against your immediately preceding tournament's | Needs history |
| Serial Finalist | Reached the Final in 3+ different tournaments | Count distinct tournaments where this player actually played the Final (`round === 99`), >= 3; tournaments without a Final do not count | Needs history |
| The Dynasty | Won 2 tournaments back-to-back | Rank 1 in two tournaments that are chronologically adjacent in this player's history — no other tournament of theirs in between | Needs history |
| Fresh Blood | Won a tournament on your very first recorded appearance | Rank 1 in the earliest tournament this player has any result in | Needs history |
| Familiar Faces | Played the same opponent across 2+ different tournaments | Count distinct tournaments where a given opponent `player_name` also appears in one of your matches, >= 2 for any single opponent | Needs history |

## A few more, same constraints

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Underdog | Won the Final without having led the standings after qualifying | Pre-Final rank is not 1, but Final `position === 1` | Ready |
| Against All Odds | Won a game with the lowest TR of any winner in that tournament | Compare your winning `terraform_rating` against every other winner's, same tournament | Ready |

## Maybe

Promising ideas, not committed to yet — revisit once the confirmed catalog above is further along.

| Name | Achievement | How it's computed | Status |
|---|---|---|---|
| Clean Slate | Played all three qualifying rounds without facing the same opponent twice | Union of opponents faced across all three qualifying rounds contains no duplicate `player_name` — the same check `alreadyPlayed`/`priorOpponents` already performs during pairing, read back from recorded matches afterward | Ready |
| Comeback Trail | Finished worse than you started, then better by the end of a tournament | `roundPlacements`: Round 2 is numerically worse (higher) than both Round 1 and Round 3, and Round 3 beats Round 1 — a genuine dip-then-recovery, not just a steady climb (which Growth Mindset already covers via TR) | Ready |
| Three-Peat | Played the same named recurring event three years running | Three tournaments sharing a name prefix (e.g. "Swedish Championship"), consecutive editions by `event_date`, this player appears in all three | Needs history |

---

## Open questions

- **Mercy Rule's exact threshold** — "win a game with 30 plus TR" was read as margin of victory,
  not raw TR; confirmed.
- **Milestone Marathon / Award Collector thresholds** — 5/15/30/60/100/150/250 is a first guess,
  not yet checked against the 3–12 games/year typical player assumption from
  `achievement-progression-plan.md`.
- **Founding Member** — floated as an idea (played in the very first tournament ever recorded),
  but reconsidered as possibly scoped to one specific recurring event (e.g. everyone who played
  the first-ever Swedish Championship) instead of a generic system-wide rule. Not written up here
  yet since the exact scope isn't settled — would likely end up as a one-off, organizer-defined
  award (see "Event day," above) rather than a computed achievement every tournament could earn.
- **Naming and artwork** — both explicitly deferred. This document exists to lock down the
  mechanics first.
