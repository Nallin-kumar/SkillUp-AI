from extractor import extract_skills


text = """
Backend development RESTful APIs Database integration
Java EE Performance optimization Version control (e.g., Git)
"""

skills = extract_skills(text)

print("Extracted skills:")
print(skills)