import json
import sys
import ollama


# =========================
# Configuration
# =========================

EVIDENCE_FILE = "data/processed/evidence_package.json"
OUTPUT_FILE = "data/processed/current_skill_explanation.json"

MODEL_NAME = "qwen3:8b"


# =========================
# Load evidence
# =========================

def load_evidence():

    with open(
        EVIDENCE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================
# Find selected skill
# =========================

def find_skill(evidence_package, selected_skill):

    for skill_data in evidence_package:

        if skill_data["skill"].lower() == selected_skill.lower():

            return skill_data

    return None


# =========================
# Generate explanation
# =========================

def generate_explanation(skill_data):

    skill = skill_data["skill"]
    demand = skill_data["demand_percentage"]
    priority = skill_data["priority"]
    jobs_analyzed = skill_data.get("jobs_analyzed", 0)
    jobs_mentioning = skill_data.get("jobs_mentioning", 0)
    evidence = skill_data["evidence"]

    # Build evidence text

    evidence_text = ""

    for index, item in enumerate(
        evidence,
        start=1
    ):

        evidence_text += f"""
--- Evidence {index} ---
Job Title: {item["title"]}
Location: {item["location"]}
Skills: {item["skills"]}
Job Description:
{item["job_description"][:1000]}
"""


    # =========================
    # Grounded LLM prompt
    # =========================

    prompt = f"""
You are a skill-gap analysis assistant.

Your task is to explain ONE curriculum skill gap using ONLY
the market data and retrieved job-posting evidence provided below.

You are NOT a general-purpose career advisor.

========================
MARKET DATA
========================

Skill: {skill}
Jobs analyzed: {jobs_analyzed}
Jobs mentioning this skill: {jobs_mentioning}
Market demand: {demand:.2f}%
Priority: {priority}

Curriculum coverage:
This skill is NOT covered by the current curriculum.

========================
RETRIEVED JOB EVIDENCE
========================

{evidence_text}

========================
GROUNDING RULES
========================

1. Use ONLY information explicitly present in the MARKET DATA
   or RETRIEVED JOB EVIDENCE.

2. Do NOT use prior knowledge or outside knowledge.

3. Do NOT invent technologies, tools, services, certifications,
   frameworks, architectures, practices, or concepts.

4. A recommendation is allowed ONLY when the recommended topic
   or technology is explicitly mentioned in the retrieved evidence.

5. Do NOT recommend something merely because it is commonly
   associated with the missing skill.

6. Do NOT expand abbreviations or concepts using outside knowledge
   unless the evidence itself provides that expansion.

7. Do NOT turn a job responsibility into a recommendation unless
   that responsibility or topic is explicitly supported by the
   evidence.

8. Do NOT recommend certifications unless a certification is
   explicitly mentioned in the retrieved evidence.

9. Do NOT combine multiple evidence items to invent a new
   technology or concept.

10. If the evidence does not clearly support a recommendation,
    return an empty recommendation list.

11. If the evidence does not establish why the skill matters,
    write exactly:

    "Not established by the provided evidence."

12. The market demand percentage comes from the market dataset.
    It must NOT be calculated from the retrieved evidence documents.

13. Do NOT claim that the retrieved evidence represents all jobs.

14. Do NOT claim that a skill is universally required.

========================
RECOMMENDATION RULE
========================

Before adding ANY curriculum recommendation, ask:

"Is this exact technology, topic, or concept explicitly present
in the retrieved evidence?"

If YES:
    It may be included.

If NO:
    Do NOT include it.

========================
OUTPUT FORMAT
========================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "skill": "{skill}",
    "why_gap": "Short explanation of why this is a curriculum gap.",
    "why_it_matters": "Short explanation based only on the provided evidence.",
    "curriculum_recommendation": [
        "Recommendation 1",
        "Recommendation 2"
    ],
    "evidence_used": [1, 2, 3]
}}

Additional requirements:

- "curriculum_recommendation" must be [] when evidence is insufficient.
- "evidence_used" may contain only evidence numbers that actually
  support the generated explanation or recommendation.
- Keep explanations concise.
- Do not use Markdown.
- Do not include ```json.
- Do not include any text before or after the JSON.
"""


    response = ollama.chat(
    model=MODEL_NAME,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    format="json",
    think=False,
    )

    response_text = response["message"]["content"].strip()

    if not response_text:

        raise RuntimeError(
            "Qwen returned an empty response."
        )

    return json.loads(
        response_text
    )

# =========================
# Main
# =========================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage: python app/llm/explain_gaps.py \"Skill Name\""
        )

        sys.exit(1)

    selected_skill = sys.argv[1]

    evidence_package = load_evidence()

    skill_data = find_skill(
        evidence_package,
        selected_skill
    )

    if skill_data is None:

        print(
            f"Skill not found in evidence package: {selected_skill}"
        )

        sys.exit(1)

    explanation = generate_explanation(
        skill_data
    )

    print(
        json.dumps(
            explanation,
            ensure_ascii=False
        )
    )