# Build plan — Historical weather reports for insurance claims

Size: **First version**. The smallest product a real person can use end to end, built well enough that you can learn from their use of it.

A starting plan in five phases. Tick them off as you go, rewrite them freely, and put your own decisions at the bottom.

## 1. Plan
- [ ] Restate the idea and who it is for in your own words, and list what you are assuming.
- [ ] Choose the stack and note why. Ask the person if two choices are close.
- [ ] Rewrite phases 2 to 5 below for this project.
- Done when: the person has read the plan and agreed.

## 2. Foundation
- [ ] A conventional stack for the problem, running locally with one command.
- Done when: the project runs locally with one command.

## 3. Core
- [ ] The whole path a user takes, with real data stored properly. Accounts and payments only if the idea cannot be tested without them.
- [ ] Target: A deterministic PDF generator that takes one address + loss date and produces the $9.99 report for a single region, closing the four gaps the sample shows (station-pinned measurements, distance-and-bearing proximity, Storm Events database, hail/lightning feeds) — then sell a handful against the existing StormRecord report to see if claims adjusters pay.
- Done when: the smallest thing worth building first works.

## 4. Harden
- [ ] Handle the failures a user will actually meet. Tests for the core path.
- Done when: the person is comfortable putting it in front of someone.

## 5. Ship and learn
- [ ] Deploy it somewhere real and measure the stop condition from the brief.
- [ ] Measure: Legally issues
- Done when: there is evidence for or against the idea.

## Decisions

_Record choices and the reasons for them here._