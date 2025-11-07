from google import genai

client = genai.Client(api_key="AIzaSyCgRmcXV4blwbEKa7BhSvWEjKb-cya7c2Y")

prompt = """
You are given four personas. Analyze them based on their values, challenges, and attitudes toward technology and energy. Your task is to generate synthetic data for alteast 6 more personals which I will then feed to a model. Generate data in a format that is most easily feedable to another model, keep the following personas but add 6  more new after analyzing current ones.

### Persona 1: Julia Lehmann
- 39 years old, married, two kids, works part-time in retail.
- Financial pressure increased, lost trust in politics.
- Seeks stability and self-sufficiency, avoids public debate.

### Persona 2: Kevin Jallow
- 45 years old, craftsman, pragmatic, family man.
- Feels life more stable now, dislikes complex rules.
- Focuses on function and affordability over ideals.

### Persona 3: Hannah Nguyen
- 28 years old, UX designer, minimalist, Berlin.
- Sustainable lifestyle, uses AI tools, values ethics in progress.
- Feels pressure from rapid change and global crises.

### Persona 4: Felix König
- 55 years old, IT consultant, tech-savvy, Munich.
- Embraced self-employment and automation.
- Values efficiency, invests in smart home and energy systems.

Now, summarize how each persona’s attitude toward technology and energy differs, and what motivates them.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

with open("gemini_persona_analysis.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Response saved to gemini_persona_analysis.txt")
