from taxonomy import SKILL_TAXONOMY


for category, skills in SKILL_TAXONOMY.items():
    print(f"\n{category}")

    for skill, aliases in skills.items():
        print(f"  {skill}: {aliases}")