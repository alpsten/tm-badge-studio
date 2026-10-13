# Achievement progression and profile rewards

Draft for discussion, 2026-10-09. This is a design proposal, not implemented behavior or a final
XP economy. The current achievement ideas come from the `different-achievements` sheet in
the original `achievements-plan.numbers` workbook; the copied repository catalog
is [achievements-plan.md](achievements-plan.md). References to tournament code and
account planning describe the source tournament project, which is separate from
this standalone artwork tool.

## Direction and audience

The expected typical player completes **3–12 recorded tournament games per year**. Those games
may use different corporations. Recognition must arrive during the first event; a player who
never wins should still make progress. Frequent players need somewhere to keep progressing.

The user wants a profile showcase of 5–10 selected achievements, expandable categories below it,
corporation progression that rewards completed games and wins, and permanent event awards.
Cosmetics and a visible overall level are proposed rewards. Exact thresholds and unlocks remain
open for balancing.

## Three things the profile can show

| Item | What it means | What contributes |
|---|---|---|
| Corporation level | Accumulated experience with one corporation | Completed games with that corporation, with a win bonus |
| Player level | Overall participation and achievements | Playing XP across all corporations, plus eligible achievement bonuses |
| Achievement collection | Specific things the player earned | Achievement rules, event participation, event results, and organizer awards |

Recommend **Player level** for the overall number because it includes both playing and
achievements. If the eventual label is **Achievement level**, explain both sources in its details.
Neither level measures competitive skill; tournament results and any future rating retain that
role.

## Corporation XP: candidate model

- A completed recorded game grants **1 XP** to the corporation used.
- A win grants **3 additional XP**, for **4 XP total**.
- A non-win never deducts XP. A scheduled game, bye, or unplayed forfeit gives no playing XP.
- Each corporation has one current progression badge. Its number represents level.
- Preserve the separate win milestones at **1, 3, 5, 10, 20, 25, and 50 wins**. These are
  accomplishments in the badge details and can unlock cosmetics; they do not redefine the level.

A curve to test is `total XP for level L = 1 + L × (L − 1)`, for `L >= 1`.
These thresholds are cumulative. The gaps grow gradually, and the formula has no final level.

| Level | Total XP | Games if none are wins | Games if all are wins |
|---|---:|---:|---:|
| 1 | 1 | 1 | 1 |
| 2 | 3 | 3 | 1 |
| 3 | 7 | 7 | 2 |
| 4 | 13 | 13 | 4 |
| 5 | 21 | 21 | 6 |
| 10 | 91 | 91 | 23 |
| 20 | 381 | 381 | 96 |

With this candidate curve, a first-game win immediately reaches level 2. That is intentional in
this draft, but should be reviewed alongside the first-event experience. There is no requirement
to stop at every level. Carry all surplus XP forward.

Examples, **assuming every game uses the same corporation**, starting from zero:

| Completed games | Wins | Corporation XP | Resulting level |
|---:|---:|---:|---:|
| 3 | 0 | 3 | 2 |
| 12 | 0 | 12 | 3 |
| 12 | 3 | 21 | 5 |
| 12 | 12 | 48 | 7 |
| 48 | 12 | 84 | 9 |

These are scenarios, not expected annual outcomes. Switching corporations spreads that XP among
their badges. At 3–12 total games per year, one corporation's later levels can take many years;
that is why the overall player track and event badges also matter.

## Levels and visual stages

Allow levels to keep increasing, but create artwork for selected milestones. A finite collection
of borders, crests, small wings, and ascended wings can support many numerical levels.

Do not reset XP or the visible lifetime level when wings or another stage unlock. If an internal
stage uses a local rank, keep lifetime level visible so an upgrade does not look like lost
progress. A prestige reset is not needed for the initial system.

Start with a few visual stages, then add more as actual players approach them. Beyond the latest
artwork milestone, the level and XP keep increasing using the existing stage's artwork. Do not
promise a distinct cosmetic for every level. Existing rank plates need support for all displayed
levels, not just the current win milestone numbers, including multi-digit values.

Distinguish a badge's verified number and award identity from optional cosmetic decoration.
Players can select previously unlocked cosmetics without changing their recorded level.

## Overall player progression

Proposed accounting:

`overall XP = completed games + (3 × wins) + eligible achievement bonuses`

A win with Ecoline therefore adds 4 to Ecoline XP and 4 to the overall playing total. It does not
add 8 to the overall total. Switching corporations preserves overall progress.

Achievement bonuses contribute only to overall XP. They do not accelerate corporation XP, and
level-ups or cosmetic unlocks do not themselves generate XP. This avoids a reward loop.

Keep achievement bonus values and the overall level curve undecided until the catalog has been
simulated. In particular, one result can earn several achievements at once. Test that first-event
bundle before selecting the thresholds. Ordinary participation should remain a meaningful source
of progress after the easy achievements are complete.

Proposed bonus rules:

- Credit each eligible achievement definition once per player. Multiple display categories do
  not mean multiple awards or bonuses; `The Specialist` is one definition.
- A corporation win milestone can be eligible once per corporation and milestone.
- Recurring event editions can each award a collectible badge. Their bonus policy is separate:
  initially favor first-time participation/champion bonuses and lifetime attendance/win
  milestones over paying the same generic achievement bonus every event.
- Purchase-related awards can remain collectibles without granting progression XP.
- General levels and cosmetics should be reachable through continued participation. Specific
  champion titles and commemorative artwork can require the relevant accomplishment.

## Rewards and event editions

Useful unlocks include avatar frames, profile banners/backgrounds, showcase decoration, optional
badge ornament styles, and display titles. A visible player level can itself be the initial
reward; more cosmetics can arrive later. Some cosmetics can unlock directly from a particular
achievement without a level requirement.

Keep tournament participation, results, statistics, history, accessibility options, basic profile
editing, and the normal showcase of up to ten earned achievements available regardless of level.
No XP multipliers or gameplay benefits are proposed.

Event awards identify the specific tournament edition. For example:

- **Swedish Championship 2027 — Champion:** a permanent award with unique event artwork. Display
  “1 of 1” only when there is exactly one verified recipient for that edition.
- **Swedish Championship 2027 — Participant:** shared commemorative artwork for qualifying
  participants, with the participation rule defined by that event.
- **Swedish Championship 2027 — Volunteer:** an organizer-confirmed award.

Different years remain distinct collectibles. Total XP cannot unlock someone else's champion
award or its exclusive identifying artwork. Cosmetic unlocks and numerical levels are separate
from these historical honors.

## Profile display and loading

Show the player's chosen and ordered 5–10 achievements prominently, with a maximum of ten and
support for fewer selections. Keep featured achievements in their normal categories too.

Below the showcase, use expandable Corporations, Tournament achievements, Game achievements,
Cross-tournament achievements, and Community & events sections. Initially fetch the showcase
images and category counts; request category images only when the section is opened, then load
further images as needed. Collapsing a section is a browsing behavior, not a privacy setting.

Show one current progression badge per corporation, with XP, win milestones, and history in its
details. Event awards remain separately selectable, with event name and year visible.

## Before implementation

1. Compare the candidate curve against players with 3, 6, and 12 annual games, plus frequent
   players, both corporation specialists and players who change corporations. Include zero wins.
2. Simulate first-event achievement bundles and later years before choosing overall XP bonuses
   and thresholds. Check both time to first reward and time to later visual stages.
3. Choose the first few cosmetic milestones, and whether level 2 on a first-game win feels right.
4. Define which historical events qualify, how awards are backfilled, and how corrected results
   update XP. Award records must retain their source and prevent repeat processing from granting
   duplicate XP. Routine play cannot reduce XP; correcting an invalid result is a separate case.
5. Keep thresholds and achievement bonus rules versioned. Review effects on earned levels and
   cosmetics before changing an economy that has already been released.

Design reference: ArenaNet describes achievement-point rewards including cosmetic skins and
titles in [New Account Achievement Rewards Incoming](https://www.guildwars2.com/en/news/new-account-achievement-rewards-incoming/).
That is an example of the reward pattern, not evidence for this draft's scoring or thresholds.
