# SkillAlign AI

AI-assisted skill gap analysis for aligning skill development curricula with industry requirements and emerging job-market demand.

---

## Problem Statement

**Government of Maharashtra — Problem Statement ID 26134**

> Challenges in aligning skill development programs with industry requirements and emerging job market demands

SkillAlign AI addresses this problem by comparing skills demanded in job postings against the skills covered by an existing curriculum.

The system identifies missing skills, prioritizes them using market demand, retrieves supporting job-posting evidence, and uses an LLM to generate grounded explanations and curriculum recommendations.

---

## What SkillAlign AI Does

The current V1 prototype analyzes:

- **Job Role:** Java Developer
- **Location:** Maharashtra
- **Curriculum:** Java Full Stack Developer

The system processes a sample of relevant job postings and produces:

1. Market-demanded skills
2. Curriculum-covered skills
3. Missing skills
4. Market demand percentage
5. Gap priority
6. Supporting job-posting evidence
7. AI-generated explanation
8. Evidence-supported curriculum recommendations

---

## Current V1 Results

For the current prototype:

| Metric | Result |
|---|---:|
| Jobs analyzed | 72 |
| Market skills | 36 |
| Curriculum-covered skills | 21 |
| Missing skills | 15 |

Examples of identified gaps:

| Skill | Market Demand | Priority |
|---|---:|---|
| Microservices | 47.22% | Medium |
| AWS | 18.06% | Medium |
| JSP | 15.28% | Medium |
| Apache Kafka | 13.89% | Low |
| Azure | 9.72% | Low |

---

# Architecture

```text
Indian Job Market Dataset
            |
            v
   Job Role + Location
       Filtering
            |
            v
 Skill Extraction & Normalization
            |
            v
     Market Skill Demand
            |
            v
   Existing Curriculum
            |
            v
      Skill Gap Engine
            |
            v
   Missing Skills + Priority
            |
            v
    Qdrant Semantic Search
            |
            v
      Evidence Package
            |
            v
        Qwen 3 8B
            |
            v
   Structured AI Explanation
            |
            v
      Streamlit Dashboard