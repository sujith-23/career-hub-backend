import json
import shutil
from pathlib import Path

DATA_FILE = Path("data/seed_data.json")
BACKUP_FILE = Path("data/seed_data-before-salary.json")


# Salary ranges are broad India-market estimates.
# They are intentionally ranges because actual salary depends on
# role, company, location, skills, experience and market conditions.
SALARY_RULES = {
    # Engineering / Technology
    "cse": ("₹3–6 LPA", "₹6–12 LPA", "₹12–25+ LPA"),
    "aids": ("₹3–6 LPA", "₹6–12 LPA", "₹12–25+ LPA"),
    "aiml": ("₹4–7 LPA", "₹8–16 LPA", "₹16–30+ LPA"),
    "it": ("₹3–6 LPA", "₹6–12 LPA", "₹12–24+ LPA"),
    "cybersecurity": ("₹3–6 LPA", "₹6–14 LPA", "₹14–28+ LPA"),
    "datascience": ("₹4–8 LPA", "₹8–16 LPA", "₹16–30+ LPA"),
    "ece": ("₹3–6 LPA", "₹6–12 LPA", "₹12–24+ LPA"),
    "eee": ("₹3–5 LPA", "₹5–10 LPA", "₹10–20+ LPA"),
    "mechanical": ("₹3–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "civil": ("₹3–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "chemical": ("₹3–6 LPA", "₹6–12 LPA", "₹12–22+ LPA"),
    "aeronautical": ("₹3–6 LPA", "₹6–12 LPA", "₹12–22+ LPA"),
    "aerospace": ("₹4–7 LPA", "₹7–14 LPA", "₹14–25+ LPA"),
    "automobile": ("₹3–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "mechatronics": ("₹3–6 LPA", "₹6–12 LPA", "₹12–22+ LPA"),
    "robotics": ("₹4–7 LPA", "₹7–14 LPA", "₹14–28+ LPA"),
    "biotech": ("₹3–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "biomedical": ("₹3–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "agricultural": ("₹3–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "mining": ("₹4–7 LPA", "₹7–14 LPA", "₹14–25+ LPA"),
    "petroleum": ("₹5–8 LPA", "₹8–16 LPA", "₹16–30+ LPA"),
    "foodtech": ("₹3–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "textile": ("₹3–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "metallurgical": ("₹3–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "marine": ("₹5–8 LPA", "₹8–16 LPA", "₹16–28+ LPA"),

    # Degree
    "bsc_cs": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "bsc_physics": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "bsc_maths": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "bsc_stats": ("₹3–6 LPA", "₹6–12 LPA", "₹12–22+ LPA"),
    "bsc_datascience": ("₹3–7 LPA", "₹7–14 LPA", "₹14–25+ LPA"),
    "bca": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "bba": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),

    # Medical
    "mbbs": ("₹6–12 LPA", "₹10–20 LPA", "₹20–40+ LPA"),
    "bds": ("₹3–6 LPA", "₹6–12 LPA", "₹12–25+ LPA"),
    "bams": ("₹3–6 LPA", "₹6–12 LPA", "₹12–20+ LPA"),
    "bhms": ("₹3–6 LPA", "₹6–12 LPA", "₹12–20+ LPA"),
    "bums": ("₹3–6 LPA", "₹6–12 LPA", "₹12–20+ LPA"),

    # Pharmacy / Nursing
    "bpharm": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "pharmd": ("₹3–6 LPA", "₹6–10 LPA", "₹10–18+ LPA"),
    "bscnursing": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "gnm": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),

    # Allied health
    "bpt": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "bmlt": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
    "radiology": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "ottech": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
    "optometry": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "dialysis": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
    "cardiaccare": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "respiratory": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "emt": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),

    # Commerce / Management
    "bcomgeneral": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "bcomcomputers": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "bcomhonours": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "bcomaccfin": ("₹3–6 LPA", "₹6–12 LPA", "₹12–20+ LPA"),
    "bcombankins": ("₹3–6 LPA", "₹6–12 LPA", "₹12–20+ LPA"),
    "bba": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "bbm": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "ca": ("₹6–10 LPA", "₹10–20 LPA", "₹20–40+ LPA"),
    "cma": ("₹5–9 LPA", "₹9–16 LPA", "₹16–30+ LPA"),
    "cs": ("₹5–9 LPA", "₹9–16 LPA", "₹16–30+ LPA"),

    # Law
    "llb": ("₹3–6 LPA", "₹6–12 LPA", "₹12–25+ LPA"),

    # Journalism / Media
    "journalism": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "hotelmanagement": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "traveltourism": ("₹2.5–5 LPA", "₹5–8 LPA", "₹8–15+ LPA"),
    "eventmanagement": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),

    # Polytechnic
    "dme": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
    "dce": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
    "deee": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
    "dece": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
    "dcse": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "daiml": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "daids": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),
    "dit": ("₹2.5–5 LPA", "₹5–9 LPA", "₹9–16+ LPA"),
    "dcybersecurity": ("₹2.5–5 LPA", "₹5–10 LPA", "₹10–18+ LPA"),

    # ITI
    "electrician": ("₹1.8–3 LPA", "₹3–5 LPA", "₹5–8+ LPA"),
    "fitter": ("₹1.8–3 LPA", "₹3–5 LPA", "₹5–8+ LPA"),
    "welder": ("₹1.8–3 LPA", "₹3–5 LPA", "₹5–8+ LPA"),
    "turner": ("₹1.8–3 LPA", "₹3–5 LPA", "₹5–8+ LPA"),
    "machinist": ("₹1.8–3 LPA", "₹3–5 LPA", "₹5–8+ LPA"),
    "copa": ("₹2–4 LPA", "₹4–7 LPA", "₹7–12+ LPA"),

    # Government / defence
    "nda": ("₹7–10 LPA", "₹10–15 LPA", "₹15–25+ LPA"),
    "ndaprep": ("₹7–10 LPA", "₹10–15 LPA", "₹15–25+ LPA"),
    "railways": ("₹3–6 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "ssc": ("₹3–6 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "police": ("₹3–6 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "govbanking": ("₹4–7 LPA", "₹7–12 LPA", "₹12–18+ LPA"),
    "stategovt": ("₹3–6 LPA", "₹5–9 LPA", "₹9–15+ LPA"),
    "postal": ("₹2.5–5 LPA", "₹4–7 LPA", "₹7–12+ LPA"),
}


def make_salary(fresher, mid_level, senior):
    return {
        "fresher": fresher,
        "midLevel": mid_level,
        "senior": senior,
        "note": (
            "Indicative India salary range. Actual salary varies by "
            "role, company, location, skills and experience."
        )
    }


def update_node(node, course_id):
    if not isinstance(node, dict):
        return 0, 0

    updated = 0
    not_found = 0

    # Update this course/path if a rule exists
    if course_id in SALARY_RULES:
        f, m, s = SALARY_RULES[course_id]
        node["salary"] = make_salary(f, m, s)
        updated += 1

    # Recursively process children
    children = node.get("children")

    if isinstance(children, dict):
        for child_id, child_node in children.items():
            u, n = update_node(child_node, child_id)
            updated += u
            not_found += n

    return updated, not_found


def main():
    if not DATA_FILE.exists():
        print("ERROR: data/seed_data.json not found.")
        return

    # Create backup
    shutil.copy2(DATA_FILE, BACKUP_FILE)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0

    for stream_id, stream in data.items():
        if not isinstance(stream, dict):
            continue

        paths = stream.get("paths", {})

        if not isinstance(paths, dict):
            continue

        for path_id, path in paths.items():
            u, _ = update_node(path, path_id)
            updated += u

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )
        f.write("\n")

    print()
    print("=" * 40)
    print("SALARY UPDATE SUCCESSFUL")
    print("=" * 40)
    print("Courses/paths updated :", updated)
    print("Backup                :", BACKUP_FILE)
    print("=" * 40)


if __name__ == "__main__":
    main()