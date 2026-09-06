# SkillUp AI

AI-powered skill gap analysis for aligning skill development curricula with real-world industry requirements and emerging job market demand.

---

## Problem Statement

### Challenges in aligning skill development programs with industry requirements and emerging job market demands

Skill development programs can become outdated as industry requirements and job-market technologies evolve.

SkillUp AI addresses this problem by comparing:

> **What the industry currently demands**  
> against  
> **What a training curriculum currently teaches**

The system identifies missing skills, prioritizes them based on market demand, retrieves supporting job-posting evidence, and uses a local LLM to explain why the missing skills matter.

---

# What is SkillUp AI?

SkillUp AI is a GenAI/RAG-based prototype that performs **industry-driven curriculum skill gap analysis**.

A user selects:

- Job Role
- Location
- Pre-loaded Curriculum

The system then:

1. Finds relevant job postings from the job-market dataset.
2. Extracts and normalizes skills from those jobs.
3. Calculates the market demand for each skill.
4. Compares market skills against the selected curriculum.
5. Identifies missing skills.
6. Prioritizes the missing skills using market demand.
7. Retrieves supporting job-posting evidence using semantic search.
8. Uses **Qwen 3 8B** through Ollama to generate an explanation for a selected skill gap.
9. Displays the results through an interactive Streamlit dashboard.

---

# Current Version

## V2 Prototype — Functional

The current version supports:

- Dynamic job-role selection
- Dynamic location selection
- Multiple pre-loaded curricula
- Expanded skill taxonomy
- Skill extraction and normalization
- Market skill-demand analysis
- Curriculum vs market comparison
- Priority-based skill gaps
- Qdrant vector search
- Job-posting evidence retrieval
- On-demand LLM explanations
- Streamlit dashboard
- Plotly visualizations

The LLM is intentionally executed **on demand for a selected skill** instead of generating explanations for every gap during analysis.

This significantly reduces unnecessary LLM calls and makes the application much faster to use.

---

# System Architecture

```text
                    ┌──────────────────────┐
                    │   Job Market Dataset │
                    │      ~98K Jobs       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Job Role + Location  │
                    │      Filtering        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Skill Extraction   │
                    │   & Normalization     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Market Skill Demand  │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
   ┌──────────────────────┐          ┌──────────────────────┐
   │ Existing Curriculum  │          │  Job Posting Data    │
   └──────────┬───────────┘          └──────────┬───────────┘
              │                                 │
              ▼                                 ▼
   ┌──────────────────────┐          ┌──────────────────────┐
   │   Skill Gap Engine   │          │   Qdrant Vector DB   │
   └──────────┬───────────┘          └──────────┬───────────┘
              │                                 │
              │                                 ▼
              │                      ┌──────────────────────┐
              │                      │ Evidence Retrieval   │
              │                      └──────────┬───────────┘
              │                                 │
              └────────────────┬────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │    Skill Gap UI      │
                    │     Streamlit        │
                    └──────────┬───────────┘
                               │
                      User selects gap
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Qwen 3 8B        │
                    │       Ollama         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ AI Skill Explanation │
                    │ + Recommendations    │
                    └──────────────────────┘