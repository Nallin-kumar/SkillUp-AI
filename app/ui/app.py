import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# Project Path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

APP_DIR = PROJECT_ROOT / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from skills.taxonomy import SKILL_TAXONOMY


# ============================================================
# Configuration
# ============================================================

GAP_REPORT = Path("data/processed/skill_gap_report.csv")
EVIDENCE_FILE = Path("data/processed/evidence_package.json")

# ============================================================
# Analysis Configuration
# ============================================================

st.subheader("Analysis Configuration")


# ------------------------------------------------------------
# Available Job Titles
# ------------------------------------------------------------

JOBS_FILE = Path(
    "data/raw/jobs/indian-job-market-dataset-2025.xlsx"
)

COURSES_DIR = Path(
    "data/raw/courses"
)


@st.cache_data
def load_job_titles():
    jobs_df = pd.read_excel(
        JOBS_FILE,
        usecols=["title"],
    )

    titles = (
        jobs_df["title"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    return sorted(
        titles.unique().tolist()
    )


# ------------------------------------------------------------
# Available Locations
# ------------------------------------------------------------

AVAILABLE_LOCATIONS = [
    "Maharashtra",
    "Karnataka",
    "Telangana",
    "Tamil Nadu",
    "Delhi NCR",
    "Gujarat",
]


# ------------------------------------------------------------
# Available Courses
# ------------------------------------------------------------

@st.cache_data
def load_courses():
    courses = []

    for course_file in COURSES_DIR.glob("*.csv"):

        courses.append({
            "name": course_file.stem.replace(
                "_",
                " "
            ).title(),
            "file": course_file.name,
        })

    return courses


# ------------------------------------------------------------
# Load configuration options
# ------------------------------------------------------------

job_titles = load_job_titles()
courses = load_courses()


# ------------------------------------------------------------
# Configuration UI
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)


with col1:

    selected_role = st.selectbox(
        "Job Title",
        job_titles,
        index=(
            job_titles.index("Java Developer")
            if "Java Developer" in job_titles
            else 0
        ),
    )


with col2:

    selected_location = st.selectbox(
        "Location",
        AVAILABLE_LOCATIONS,
        index=(
            AVAILABLE_LOCATIONS.index("Maharashtra")
            if "Maharashtra" in AVAILABLE_LOCATIONS
            else 0
        ),
    )


with col3:

    selected_course = st.selectbox(
        "Course",
        courses,
        format_func=lambda course: course["name"],
    )


CURRICULUM_NAME = selected_course["name"]
CURRICULUM_FILE = selected_course["file"]


# ============================================================
# Run Analysis Pipeline
# ============================================================

def run_analysis_pipeline(
    role,
    location,
    curriculum_file,
):

    scripts = [
        (
            "Market Skill Analysis",
            [
                "app/skills/analyze_skills.py",
                role,
                location,
            ],
        ),
        (
            "Skill Gap Calculation",
            [
                "app/analysis/gap_calculator.py",
                role,
                location,
                curriculum_file,
            ],
        ),
        (
            "Evidence Preparation",
            [
                "app/ingestion/prepare_evidence.py",
                role,
                location,
            ],
        ),
        (
            "Qdrant Indexing",
            [
                "app/rag/index_jobs.py",
                role,
                location,
            ],
        ),
        (
            "Evidence Package",
            [
                "app/rag/build_evidence_package.py",
                role,
                location,
            ],
        ),
        
    ]

    for step_name, command in scripts:

        with st.status(
            f"Running: {step_name}...",
            expanded=True,
        ) as status:

            try:

                result = subprocess.run(
                    [
                        sys.executable,
                        *command,
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=True,
                )

                if result.stdout:
                    st.code(
                        result.stdout
                    )

                if result.stderr:
                    st.caption(
                        result.stderr
                    )

                status.update(
                    label=f"Completed: {step_name}",
                    state="complete",
                )

            except subprocess.CalledProcessError as error:

                if error.stdout:
                    st.code(
                        error.stdout
                    )

                if error.stderr:
                    st.error(
                        error.stderr
                    )

                status.update(
                    label=f"Failed: {step_name}",
                    state="error",
                )

                return False

    return True


# ============================================================
# Generate AI Explanation for Selected Skill
# ============================================================

def generate_skill_explanation(skill):

    result = subprocess.run(
        [
            sys.executable,
            "app/llm/explain_gaps.py",
            skill,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    output = result.stdout.strip()

    if not output:

        raise RuntimeError(
            "The AI model returned an empty response."
        )

    try:

        return json.loads(output)

    except json.JSONDecodeError as error:

        raise RuntimeError(
            f"The AI model returned invalid JSON:\n\n{output}"
        ) from error
    

st.divider()


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="SkillAlign AI",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# Data loading
# ============================================================

@st.cache_data
def load_gap_report():
    return pd.read_csv(GAP_REPORT)



@st.cache_data
def load_evidence():
    with open(EVIDENCE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# Analyze Button
# ============================================================

if st.button(
    "Analyze",
    type="primary",
    use_container_width=True,
):

    with st.spinner(
        "Running SkillAlign AI analysis..."
    ):

        success = run_analysis_pipeline(
            selected_role,
            selected_location,
            CURRICULUM_FILE,
        )

    if success:

        load_gap_report.clear()
        load_evidence.clear()

        st.session_state.pop(
            "current_skill_explanation",
            None,
        )

        st.rerun()


# ============================================================
# Validate required files
# ============================================================

required_files = [
    GAP_REPORT,
    EVIDENCE_FILE,
]

missing_files = [
    str(file)
    for file in required_files
    if not file.exists()
]

if missing_files:
    st.error("SkillAlign AI could not load the required processed data.")

    st.write("Missing files:")

    for file in missing_files:
        st.code(file)

    st.info(
        "Run the SkillAlign AI processing pipeline first, "
        "then restart the Streamlit application."
    )

    st.stop()


# ============================================================
# Load application data
# ============================================================

try:
    gap_df = load_gap_report()
    evidence_package = load_evidence()

except Exception as error:
    st.error("An error occurred while loading SkillAlign AI data.")
    st.exception(error)
    st.stop()


# ============================================================
# Basic data validation
# ============================================================

required_columns = {
    "role",
    "location",
    "skill",
    "job_count",
    "demand_percentage",
    "gap",
    "gap_score",
    "priority",
}

missing_columns = required_columns - set(gap_df.columns)

if missing_columns:
    st.error("The skill gap report has an unexpected schema.")

    st.write("Missing columns:")

    for column in sorted(missing_columns):
        st.code(column)

    st.stop()


# ============================================================
# Prepare lookup maps
# ============================================================

evidence_map = {
    item["skill"]: item
    for item in evidence_package
}

# LLM output can occasionally miss the "skill" field.
# Evidence package preserves the correct skill order, so use it
# as the source of truth when building the explanation map.


# ============================================================
# Header
# ============================================================

st.title("SkillAlign AI")

st.subheader(
    f"{selected_role} Skill Gap Analysis — {selected_location}"
)

st.write(
    "SkillAlign AI compares skills demanded by the analyzed job market "
    "with skills covered by the selected curriculum and identifies "
    "the most important curriculum gaps."
)


# ============================================================
# Current analysis context
# ============================================================

st.info(
    f"**Current analysis:** "
    f"{selected_role} · {selected_location} · {CURRICULUM_NAME}"
)


# ============================================================
# Selected Curriculum
# ============================================================

st.header("Selected Curriculum")

curriculum_df = pd.read_csv(
    Path("data/raw/courses") / CURRICULUM_FILE
)

curriculum_skills = (
    curriculum_df["skill"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .tolist()
)

st.write(
    f"**{CURRICULUM_NAME}** contains "
    f"**{len(curriculum_skills)} skills**."
)

st.write(
    "These are the skills currently covered by the selected curriculum."
)

st.markdown(
    " · ".join(
        f"`{skill}`"
        for skill in curriculum_skills
    )
)



# ============================================================
# Overview metrics
# ============================================================

jobs_analyzed = gap_df["job_count"].max() / (
    gap_df["demand_percentage"].max() / 100
)

jobs_analyzed = round(jobs_analyzed)

market_skills = len(gap_df)

total_gaps = int(gap_df["gap"].sum())

curriculum_skills = int((~gap_df["gap"]).sum())

high_priority = int(
    (gap_df["priority"] == "High").sum()
)

medium_priority = int(
    (gap_df["priority"] == "Medium").sum()
)

low_priority = int(
    (gap_df["priority"] == "Low").sum()
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Jobs Analyzed",
        jobs_analyzed,
    )

with col2:
    st.metric(
        "Market Skills",
        market_skills,
    )

with col3:
    st.metric(
        "Curriculum Covers",
        curriculum_skills,
    )

with col4:
    st.metric(
        "Skill Gaps",
        total_gaps,
    )


# ============================================================
# Priority summary
# ============================================================

st.divider()

st.header("Gap Priority Overview")

priority_col1, priority_col2, priority_col3 = st.columns(3)

with priority_col1:
    st.metric(
        "High Priority",
        high_priority,
    )

with priority_col2:
    st.metric(
        "Medium Priority",
        medium_priority,
    )

with priority_col3:
    st.metric(
        "Low Priority",
        low_priority,
    )


# ============================================================
# Skill Gap Chart
# ============================================================

st.divider()

st.header("Market Skill Gaps")

st.write(
    "The chart shows skills found in the analyzed job market "
    "that are not currently covered by the curriculum."
)

gap_chart_df = gap_df[
    gap_df["gap"]
].copy()

gap_chart_df = gap_chart_df.sort_values(
    "demand_percentage",
    ascending=True,
)


if gap_chart_df.empty:

    st.success(
        "No curriculum skill gaps were identified."
    )

else:

    fig = px.bar(
        gap_chart_df,
        x="demand_percentage",
        y="skill",
        orientation="h",
        labels={
            "demand_percentage": "Market Demand (%)",
            "skill": "Skill",
        },
        title="Missing Skills Ranked by Market Demand",
        hover_data={
            "demand_percentage": ":.2f",
            "job_count": True,
            "priority": True,
        },
    )

    fig.update_layout(
        height=max(
            450,
            len(gap_chart_df) * 32,
        ),
        xaxis_title="Market Demand (%)",
        yaxis_title="",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# Gap Details
# ============================================================

if not gap_chart_df.empty:

    st.divider()

    st.header("Skill Gap Details")

    selected_skill = st.selectbox(
        "Select a missing skill",
        gap_chart_df["skill"].tolist(),
    )

    selected_gap = gap_df[
        gap_df["skill"] == selected_skill
    ].iloc[0]


    selected_evidence = evidence_map.get(
        selected_skill
    )


    # ========================================================
    # Selected skill metrics
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Market Demand",
            f"{selected_gap['demand_percentage']:.2f}%",
        )

    with col2:
        st.metric(
            "Jobs Mentioning Skill",
            int(selected_gap["job_count"]),
        )

    with col3:
        st.metric(
            "Priority",
            selected_gap["priority"],
        )

# ========================================================
# AI Explanation
# ========================================================

st.subheader("AI Analysis")

st.write(
    "Generate an evidence-grounded AI explanation for the "
    "selected skill gap."
)

if st.button(
    f"Generate AI Analysis for {selected_skill}",
    type="primary",
):

    with st.spinner(
        f"Qwen is analyzing {selected_skill}..."
    ):

        try:

            selected_explanation = generate_skill_explanation(
                selected_skill
            )

            if selected_explanation:

                st.session_state[
                    "current_skill_explanation"
                ] = selected_explanation

            else:

                st.error(
                    "AI explanation could not be generated."
                )

        except subprocess.CalledProcessError as error:

            st.error(
                "The AI explanation process failed."
            )

            if error.stdout:
                st.code(error.stdout)

            if error.stderr:
                st.error(error.stderr)

        except Exception as error:

            st.error(
                "An error occurred while generating "
                "the AI explanation."
            )

            st.exception(error)


current_explanation = st.session_state.get(
    "current_skill_explanation"
)


if (
    current_explanation
    and current_explanation.get("skill") == selected_skill
):

    st.markdown(
        "**Why is this a skill gap?**"
    )

    st.write(
        current_explanation.get(
            "why_gap",
            "No explanation available.",
        )
    )

    st.markdown(
        "**Why does it matter?**"
    )

    st.write(
        current_explanation.get(
            "why_it_matters",
            "No explanation available.",
        )
    )

    st.markdown(
        "**Curriculum Recommendations**"
    )

    recommendations = current_explanation.get(
        "curriculum_recommendation",
        [],
    )

    if recommendations:

        for recommendation in recommendations:

            st.write(
                f"• {recommendation}"
            )

    else:

        st.info(
            "No curriculum recommendation was generated "
            "from the available evidence."
        )

    evidence_used = current_explanation.get(
        "evidence_used",
        [],
    )

    if evidence_used:

        st.markdown(
            f"**Evidence Used:** "
            f"{', '.join(map(str, evidence_used))}"
        )

else:

    st.info(
        "Click the button above to generate an "
        "AI explanation for this skill."
    )


# ========================================================
# Market Evidence
# ========================================================

st.divider()

st.subheader("Market Evidence")

st.write(
    "These job postings were retrieved from the analyzed "
    "market dataset to provide supporting evidence for "
    "this skill gap."
)

if (
    selected_evidence
    and selected_evidence.get("evidence")
):

    for index, evidence in enumerate(
        selected_evidence["evidence"],
        start=1,
    ):

        similarity = evidence.get(
            "similarity",
            0,
        )

        title = evidence.get(
            "title",
            "Unknown",
        )

        with st.expander(
            f"Evidence {index} — "
            f"{title} — Similarity: {similarity:.4f}",
            expanded=False,
        ):

            st.write(
                f"**Job Title:** "
                f"{evidence.get('title', 'Unknown')}"
            )

            st.write(
                f"**Location:** "
                f"{evidence.get('location', 'Unknown')}"
            )

            st.write(
                f"**Skills:** "
                f"{evidence.get('skills', 'Not available')}"
            )

            st.write("**Job Description:**")

            st.write(
                evidence.get(
                    "job_description",
                    "Not available.",
                )
            )

else:

    st.info(
        "No supporting job evidence was retrieved."
    )


# ============================================================
# Methodology & Data Sources
# ============================================================

st.divider()

st.header("Methodology & Data Sources")

with st.expander(
    "How this analysis is calculated",
    expanded=False,
):

    st.markdown(
        f"""
### 1. Job-market data

The analysis uses the provided **Indian Job Market Dataset 2025**.

The user selects:

- **Job Role:** {selected_role}
- **Location:** {selected_location}

The resulting matching job postings form the market sample used
for this analysis.

### 2. Skill extraction

Skills are extracted and normalized using the project's
controlled skill taxonomy.

This allows different representations of skills to be compared
consistently.

### 3. Market skill demand

For each normalized skill, the system calculates how frequently
the skill appears across the analyzed job postings.

**Market Demand (%) = Jobs mentioning skill / Jobs analyzed × 100**

### 4. Curriculum comparison

The market skills are compared against the selected curriculum:

**{CURRICULUM_NAME}**

A skill is considered a gap when it appears in the analyzed
market data but is not present in the selected curriculum.

### 5. Priority

The current priority system is intentionally simple:

- **High:** ≥ 50% demand
- **Medium:** ≥ 15% demand
- **Low:** > 0% demand

The priority is based on market demand for missing skills.

### 6. Evidence retrieval

Qdrant performs semantic retrieval over the analyzed job postings
to find supporting evidence for each missing skill.

### 7. AI explanation

Qwen 3 8B generates explanations using the retrieved evidence.

The LLM explains the results; it does not calculate the market
statistics.
"""
    )


# ============================================================
# Data Source Transparency
# ============================================================

with st.expander(
    "Data source & prototype limitations",
    expanded=False,
):

    st.markdown(
        """
### Job-market dataset

The current analysis is based on the provided **Indian Job Market
Dataset 2025**.

The results represent the analyzed dataset and should not be
interpreted as a live real-time view of the entire job market.

### Curriculum

The available curricula are prototype curriculum datasets created
for demonstrating the SkillAlign AI concept.

They should not be interpreted as official curricula from a
training institution or government program unless explicitly
specified.

### Skill taxonomy

Skill extraction and normalization depend on the project's
controlled skill taxonomy.

If a technology or skill is not represented in the taxonomy,
the system may not detect it even when it appears in a job posting.

### Current prototype limitations

The quality of the analysis depends on:

- The available job-market dataset
- The selected job role and location
- The selected curriculum
- The controlled skill taxonomy
- The quality of retrieved job-posting evidence
- The generated AI explanation

The current system is a prototype intended to demonstrate the
SkillAlign AI approach rather than provide live labour-market
intelligence.
"""
    )


# ============================================================
# How SkillAlign AI Works
# ============================================================

st.divider()

st.header("How SkillAlign AI Works")

st.markdown(
    f"""
**1. Job Market Data**

Job postings are loaded from the analyzed dataset.

↓

**2. Role + Location Filtering**

The user selects a job role and location.

The system filters the job-market dataset to identify relevant
postings for **{selected_role}** in **{selected_location}**.

↓

**3. Skill Extraction & Normalization**

Job skills are mapped to the controlled skill taxonomy.

↓

**4. Market Skill Demand**

The system calculates how frequently each skill appears in the
analyzed jobs.

↓

**5. Curriculum Comparison**

Market-demanded skills are compared with the selected curriculum:

**{CURRICULUM_NAME}**

↓

**6. Skill Gap Calculation**

Skills demanded by the market but missing from the selected
curriculum become skill gaps.

↓

**7. Evidence Retrieval**

Qdrant retrieves relevant job postings for each missing skill.

↓

**8. AI Explanation**

Qwen 3 8B explains why the skill gap matters and suggests
curriculum additions supported by the retrieved market evidence.
"""
)


# ============================================================
# Architecture principles
# ============================================================

with st.expander(
    "AI architecture principles",
    expanded=False,
):

    st.markdown(
        """
SkillAlign AI separates deterministic analysis from generative AI.

**Python**

Calculates job filtering, skill demand, curriculum coverage,
gap scores, and priorities.

**Qdrant**

Retrieves semantically relevant job-posting evidence.

**Qwen 3 8B**

Generates explanations from the retrieved evidence.

This separation keeps market statistics and gap calculations
deterministic rather than allowing the LLM to calculate them.
"""
    )


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "SkillAlign AI — V2 Prototype | "
    "Market statistics and skill-gap calculations are deterministic; "
    "AI explanations are generated from retrieved market evidence."
)