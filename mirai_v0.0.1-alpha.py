#!/usr/bin/env python3
"""
Sunset Symphony — Simple Idol Manager Sim (Terminal)
Mirai Productions debut group, chosen by a futuristic potential-sensing AI.

Modes:
- practice: train stats (vocal, dance, visual, stamina, mental)
- work: gather fans (flyers / guerilla live)
- live: perform (local venue only at start)
"""

import random
import textwrap
from dataclasses import dataclass, field

# ---------------------------- Data Models ----------------------------

STATS = ["vocal", "dance", "visual", "stamina", "mental"]

@dataclass
class Idol:
    name: str
    age: int
    role: str
    blurb: str
    stats: dict = field(default_factory=dict)

    def clamp_stats(self):
        for k in STATS:
            self.stats[k] = max(1, min(100, int(self.stats[k])))

    @property
    def avg_perf(self):
        # Performance leans vocal/dance/visual, with small influence from mental/stamina
        return (
            0.30 * self.stats["vocal"]
            + 0.30 * self.stats["dance"]
            + 0.25 * self.stats["visual"]
            + 0.10 * self.stats["mental"]
            + 0.05 * self.stats["stamina"]
        )

    def short_card(self):
        s = self.stats
        return f"{self.name} ({self.age}) — {self.role}\n" \
               f"  Vocal {s['vocal']:>3} | Dance {s['dance']:>3} | Visual {s['visual']:>3} | Stamina {s['stamina']:>3} | Mental {s['mental']:>3}"

@dataclass
class GroupState:
    name: str
    agency: str
    ai_name: str
    idols: list
    day: int = 1
    funds: int = 2000
    fans: int = 40
    reputation: float = 0.0  # small modifier that grows with good lives
    last_live_report: str = ""

    def group_perf(self):
        return sum(i.avg_perf for i in self.idols) / len(self.idols)

    def group_energy(self):
        # average stamina + mental
        st = sum(i.stats["stamina"] for i in self.idols) / len(self.idols)
        me = sum(i.stats["mental"] for i in self.idols) / len(self.idols)
        return (st + me) / 2

# ---------------------------- Setup ----------------------------

def wrap(s, width=78):
    return "\n".join(textwrap.wrap(s, width=width))

def make_game():
    leader = Idol(
        name="Aoi Kisaragi",
        age=15,
        role="Leader (quiet, searching for her smile)",
        blurb=(
            "Shy and sharply observant, Aoi speaks softly like she’s afraid of taking up space. "
            "She calls herself a realist—others might say nihilistic—but something in her keeps "
            "reaching for warmth anyway. The AI chose her as leader for her steadiness under pressure. "
            "She’s learning how to smile on purpose, not by accident."
        ),
        stats={"vocal": 46, "dance": 44, "visual": 48, "stamina": 52, "mental": 60},
    )

    bubbly = Idol(
        name="Yui Tachibana",
        age=15,
        role="Mood-maker (bubbly, clumsy, sincere)",
        blurb=(
            "Yui is bright enough to light a hallway—sometimes literally, because she trips over cables. "
            "She wants to make people happy more than she wants applause. When she laughs, the room "
            "forgives everything. The AI flagged her “empathy resonance” as unusually high."
        ),
        stats={"vocal": 42, "dance": 50, "visual": 47, "stamina": 58, "mental": 48},
    )

    serious = Idol(
        name="Rina Kurosawa",
        age=16,
        role="Strategist (smart, serious, skeptical)",
        blurb=(
            "Rina learns fast, speaks precisely, and doesn’t trust dreams that can’t be measured. "
            "At first she doubts the project—an AI picking idols felt like a gimmick to her. "
            "But she can’t ignore the data: the group is improving, and something real is forming. "
            "She’ll believe in Sunset Symphony when it earns it."
        ),
        stats={"vocal": 50, "dance": 46, "visual": 45, "stamina": 50, "mental": 62},
    )

    state = GroupState(
        name="Sunset Symphony",
        agency="Mirai Productions",
        ai_name="ORACLE//MIRAI",
        idols=[leader, bubbly, serious],
        day=1,
        funds=2000,
        fans=40,
        reputation=0.0,
    )
    return state

# ---------------------------- UI Helpers ----------------------------

def header(state: GroupState):
    print("\n" + "=" * 78)
    print(f" Day {state.day}  |  {state.agency}  |  Debut Unit: {state.name}")
    print(f" AI Selector: {state.ai_name}  |  Funds: ¥{state.funds}  |  Fans: {state.fans}  |  Rep: {state.reputation:+.2f}")
    print("=" * 78)

def show_profiles(state: GroupState):
    print("\n--- Profiles: Sunset Symphony ---\n")
    for idol in state.idols:
        print(idol.short_card())
        print("  " + wrap(idol.blurb).replace("\n", "\n  "))
        print()

def show_roster(state: GroupState):
    print("\n--- Roster ---")
    for idx, idol in enumerate(state.idols, 1):
        print(f"[{idx}] {idol.short_card()}")

def choose_int(prompt, lo, hi, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        if raw.isdigit():
            v = int(raw)
            if lo <= v <= hi:
                return v
        print(f"Enter a number between {lo} and {hi}.")

def choose_from(prompt, options):
    # options is list of strings
    while True:
        print()
        for i, opt in enumerate(options, 1):
            print(f"[{i}] {opt}")
        v = choose_int(prompt, 1, len(options))
        return v - 1

# ---------------------------- Mechanics ----------------------------

def apply_fatigue(idol: Idol, stamina_cost=0, mental_cost=0):
    idol.stats["stamina"] -= stamina_cost
    idol.stats["mental"] -= mental_cost
    idol.clamp_stats()

def practice(state: GroupState):
    show_roster(state)
    print("\nPractice Mode: Train one idol, or train as a group.")
    idx = choose_int("Choose idol [1-3] or 4 for group practice: ", 1, 4)

    attr_idx = choose_from("Train which attribute? ", [s.title() for s in STATS])
    attr = STATS[attr_idx]

    # Training tuning
    base_gain = random.randint(2, 5)
    if attr in ("stamina", "mental"):
        base_gain = random.randint(2, 6)

    funds_cost = 120 if idx != 4 else 220
    if state.funds < funds_cost:
        print("\nNot enough funds for practice today.")
        return

    state.funds -= funds_cost

    if idx == 4:
        # group practice: smaller gain each, but cohesion boost to rep
        for idol in state.idols:
            gain = max(1, base_gain - 1 + random.randint(0, 2))
            idol.stats[attr] += gain
            # fatigue
            apply_fatigue(idol, stamina_cost=2, mental_cost=1)
            idol.clamp_stats()
        state.reputation += 0.03
        print(f"\nGroup practice complete! Everyone trained {attr.title()} (cost ¥{funds_cost}).")
    else:
        idol = state.idols[idx - 1]
        gain = base_gain + random.randint(0, 3)
        idol.stats[attr] += gain
        # fatigue scaled by how intense the stat is
        apply_fatigue(idol, stamina_cost=3, mental_cost=2)
        idol.clamp_stats()
        state.reputation += 0.01
        print(f"\nPractice complete! {idol.name} trained {attr.title()} +{gain} (cost ¥{funds_cost}).")

def work(state: GroupState):
    show_roster(state)
    print("\nWork Mode: Gather fans and visibility.")
    choice = choose_from("Choose activity: ", ["Hand out flyers", "Guerilla live (small pop-up performance)"])

    if choice == 0:
        # Flyers: steady fan gain, low cost, low fatigue
        funds_cost = 60
        if state.funds < funds_cost:
            print("\nNot enough funds for printing flyers.")
            return
        state.funds -= funds_cost

        # fan gain depends a bit on visual + mental (confidence)
        vis = sum(i.stats["visual"] for i in state.idols) / len(state.idols)
        men = sum(i.stats["mental"] for i in state.idols) / len(state.idols)
        gain = int(random.randint(8, 16) + (vis + men) * 0.10 + state.reputation * 4)
        gain = max(5, gain)

        state.fans += gain
        for idol in state.idols:
            apply_fatigue(idol, stamina_cost=1, mental_cost=1)

        print(f"\nFlyer run complete! +{gain} fans (cost ¥{funds_cost}).")

    else:
        # Guerilla live: bigger variance, more fatigue, bigger rep potential
        funds_cost = 140
        if state.funds < funds_cost:
            print("\nNot enough funds for transport + minimal equipment.")
            return
        state.funds -= funds_cost

        perf = state.group_perf()
        energy = state.group_energy()
        crowd_roll = random.uniform(0.85, 1.20)

        # fan gain scales with performance + a little luck, reduced if exhausted
        exhaustion_penalty = max(0, (55 - energy) * 0.12)
        gain = int((perf * 0.55 + random.randint(10, 30) + state.reputation * 10) * crowd_roll - exhaustion_penalty)
        gain = max(6, gain)

        state.fans += gain
        rep_delta = (perf - 45) / 900.0 + random.uniform(-0.01, 0.03)
        state.reputation += rep_delta

        for idol in state.idols:
            apply_fatigue(idol, stamina_cost=4, mental_cost=3)

        print(f"\nGuerilla live success! +{gain} fans (cost ¥{funds_cost}). Rep {rep_delta:+.2f}")

def live(state: GroupState):
    # Only one venue and one song at start
    venue_name = "Hoshizora Park Stage"
    capacity = 300
    song = "Sunset Protocol (Debut Ver.)"
    formations = ["Classic Triangle (Aoi center)", "Twin Wings (Yui & Rina front)", "Line-Up (equal focus)"]

    print("\nLive Mode: Choose venue, song, and formation.\n")
    print(f"Venue available: {venue_name} (Capacity {capacity})")
    print(f"Song available: {song}")

    form_idx = choose_from("Choose formation: ", formations)
    formation = formations[form_idx]

    # Basic checks / costs
    venue_cost = 350
    if state.funds < venue_cost:
        print("\nNot enough funds to set up the live (permits, equipment, staff).")
        return

    # If too exhausted, performance suffers
    perf = state.group_perf()
    energy = state.group_energy()

    # Hype is driven by fans + reputation + some randomness
    hype = (state.fans ** 0.5) * 4 + state.reputation * 20 + random.uniform(-3, 6)
    hype = max(0, hype)

    # Turnout is a function of fans and hype (with park walk-ins)
    walk_ins = random.randint(15, 60)
    expected = int(state.fans * (0.18 + min(0.22, hype / 200.0)) + walk_ins)
    turnout = max(0, min(capacity, expected))

    # Performance score: weighted by perf, boosted by hype, reduced by low energy
    energy_factor = 1.0 - max(0.0, (55 - energy) / 120.0)  # if energy < 55, penalty grows
    form_bonus = [1.02, 1.01, 1.00][form_idx]  # tiny at start
    performance_score = (perf * form_bonus) * energy_factor + random.uniform(-2.5, 2.5) + (hype / 25.0)

    # Audience satisfaction determines fan change
    satisfaction = performance_score + random.uniform(-3, 3)
    if satisfaction >= 62:
        review = "The crowd roared—people stayed to watch twice."
        fan_mult = 0.22
        rep_delta = 0.10
    elif satisfaction >= 54:
        review = "A warm reception—new faces asked for your next schedule."
        fan_mult = 0.14
        rep_delta = 0.05
    elif satisfaction >= 48:
        review = "A decent showing—some cheers, some polite claps."
        fan_mult = 0.08
        rep_delta = 0.02
    else:
        review = "Nerves showed—but you finished the song together."
        fan_mult = 0.04
        rep_delta = -0.01

    # Money and fans
    ticket_price = 400
    merch_per_head = random.randint(40, 90)
    income = turnout * (ticket_price + merch_per_head)
    state.funds += income - venue_cost

    gained_fans = int(turnout * fan_mult + random.randint(2, 12))
    lost_fans = 0
    if satisfaction < 46:
        lost_fans = int(min(state.fans * 0.03, random.randint(1, 8)))
    state.fans += gained_fans
    state.fans -= lost_fans
    state.fans = max(0, state.fans)

    # Fatigue from live
    for idol in state.idols:
        apply_fatigue(idol, stamina_cost=6, mental_cost=5)

    state.reputation += rep_delta

    report = []
    report.append(f"LIVE REPORT — {venue_name}")
    report.append(f"Song: {song}")
    report.append(f"Formation: {formation}")
    report.append("")
    report.append(f"Turnout: {turnout}/{capacity}")
    report.append(f"Group Performance: {perf:.1f}  |  Energy: {energy:.1f}  |  Hype: {hype:.1f}")
    report.append(f"Performance Score: {performance_score:.1f}  |  Satisfaction: {satisfaction:.1f}")
    report.append(f"Review: {review}")
    report.append("")
    report.append(f"Funds: +¥{income} income  -¥{venue_cost} costs  => Net {income - venue_cost:+} yen")
    report.append(f"Fans: +{gained_fans} gained  -{lost_fans} lost  => Net {gained_fans - lost_fans:+}")
    report.append(f"Reputation change: {rep_delta:+.2f}")

    state.last_live_report = "\n".join(report)
    print("\n" + "-" * 78)
    print(state.last_live_report)
    print("-" * 78)

def rest_day(state: GroupState):
    # Small recovery, costs nothing, small rep drift
    for idol in state.idols:
        idol.stats["stamina"] += random.randint(6, 10)
        idol.stats["mental"] += random.randint(5, 9)
        idol.clamp_stats()
    state.reputation = max(-1.0, state.reputation - 0.01)
    print("\nRest day: Everyone recovered some stamina and mental.")

def end_day(state: GroupState):
    state.day += 1
    # light passive fan drift
    drift = int(state.reputation * 2 + random.randint(-1, 3))
    if drift > 0:
        state.fans += drift
    state.fans = max(0, state.fans)

# ---------------------------- Main Loop ----------------------------

def main():
    random.seed()  # non-deterministic by default
    state = make_game()

    print("\nWelcome to MIRAI PRODUCTIONS — Idol Manager Sim (Terminal)\n")
    print("A futuristic AI called ORACLE//MIRAI selected three girls with hidden potential.")
    print("Their debut unit name is: SUNSET SYMPHONY\n")
    show_profiles(state)

    while True:
        header(state)
        show_roster(state)

        print("\nChoose an action:")
        print("[1] Practice (train stats)")
        print("[2] Work (gather fans)")
        print("[3] Live (perform show)")
        print("[4] Rest (recover)")
        print("[5] View Profiles")
        print("[6] View Last Live Report")
        print("[7] End Day")
        print("[0] Quit")

        choice = choose_int("\n> ", 0, 7)

        if choice == 0:
            print("\nThanks for managing Sunset Symphony. Good luck on the road to the future.\n")
            break
        elif choice == 1:
            practice(state)
        elif choice == 2:
            work(state)
        elif choice == 3:
            live(state)
        elif choice == 4:
            rest_day(state)
        elif choice == 5:
            show_profiles(state)
        elif choice == 6:
            print("\n" + (state.last_live_report or "No live performed yet."))
        elif choice == 7:
            end_day(state)
            print("\nDay ended.")

if __name__ == "__main__":
    main()
