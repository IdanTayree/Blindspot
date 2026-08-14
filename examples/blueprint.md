# Dog walker booking app — blueprint

> **Illustrative example.** A short, invented interview showing the shape of the output. A real one runs far
> longer and the answers are the user's own words, not paraphrase.

- **Status:** interview in progress · depth level **1 — absolute beginner**
- **The idea, in one line:** an app where dog walkers list when they are free and owners book them.

## The record

### Q1 — who pays, and when

**Owners pay, at the time of booking.** Walkers keep everything minus a small cut.

*Consequence:* money moves inside the app on day one, which means a payment provider, refunds when a walk is
cancelled, and a decision about who is liable when a walk does not happen. That is a large amount of work for
a first version — flagged, not resolved.

### Q2 — can someone use it without an account

**No.** Bookings and history have to be saved, and he would rather lose the browsers than lose the bookings.

*Consequence:* sign-up is on the critical path, so the sign-up screen is now the most important screen in the
product rather than an afterthought.

### Q3 — who confirms a booking

**The walker confirms.** An owner requests a time; the walker accepts or declines.

*Consequence:* a booking has states, not just a date — requested, accepted, declined, done, cancelled. That
list is the spine of both the database and the notifications.

### Q4 — what happens when a walker never responds

*Two of your answers pull against each other.* Walkers confirm every booking (Q3), and owners pay at the
moment of booking (Q1) — so an unanswered request leaves an owner charged for a walk nobody agreed to.

**His answer: hold the money, do not take it.** If the walker has not answered within two hours, the request
expires and nothing is charged.

*Consequence:* payments need an authorise-then-capture flow rather than a straight charge, and something has
to run on a timer to expire stale requests. Both were invisible before the collision surfaced them.

### Q5 — does it need to work without internet

**No.** Both sides are outdoors on phones, and everything meaningful needs the network anyway.

*Consequence:* closes off a large amount of offline-sync work. Recorded because "does it work offline" is the
question most likely to be asked later by someone who was not here.

## Progress, by quadrant

| Quadrant | Entries | How they were found | Still producing? |
|---|---:|---|---|
| Known knowns | 5 | direct questions | yes |
| Known unknowns | 2 | his own deferrals | steady |
| Unknown knowns | 1 | "obviously the walker decides" | slowing |
| Unknown unknowns | 1 | collision between Q1 and Q3 | yes |

Spawn rate: 0.6 new questions per answer — still expanding.
Estimate: roughly 20–30+ questions remaining.

## Assumptions made without asking

- English only at launch.
- Phones, not desktop. Walkers are outdoors.
- One city to begin with; no timezone handling.
- Photos of dogs are nice, not required.

## Areas not yet touched

- What happens when a walk goes wrong — injury, a lost dog, a no-show.
- Reviews and trust between strangers.
- How a walker is verified as a real person.
- Cancellations by the owner, and refunds.

## Components to build

These become the input to the harvest phase.

- Accounts and sign-in
- Availability calendar
- Booking state machine (requested → accepted → done)
- Payments with authorise-then-capture
- Scheduled expiry of unanswered requests
- Push notifications to both sides
- Maps and location
