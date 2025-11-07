import os
import json
import re
import sqlite3
import hashlib
from typing import Dict, Any, List

import streamlit as st
from PIL import Image

ARCHETYPE_PERSONAS = [
  {
    "name": "Julia Lehmann",
    "age": 39,
    "occupation": "Part-time Retail Worker",
    "location": "Suburban Area",
    "demographics": ["married", "two kids"],
    "values": ["Stability", "Self-sufficiency", "Family well-being", "Avoiding public debate"],
    "challenges": ["Financial pressure", "Loss of trust in politics", "Feeling overwhelmed by external events"],
    "attitude_technology": "Pragmatic; views technology as a tool for saving money or making daily life easier. May be cautious about complex or costly tech, preferring simple, reliable solutions.",
    "attitude_energy": "Seeks affordability and reliability in energy. Interested in solutions that reduce energy bills (e.g., energy-efficient appliances) or provide a sense of independence (e.g., small-scale home generation) to achieve self-sufficiency, with cost being a primary driver.",
    "motivation": "Protecting her family's financial security and well-being, reducing personal stress, gaining control over her immediate living environment."
  },
  {
    "name": "Kevin Jallow",
    "age": 45,
    "occupation": "Craftsman",
    "location": "Small Town",
    "demographics": ["family man"],
    "values": ["Pragmatism", "Functionality", "Affordability", "Simplicity", "Stability"],
    "challenges": ["Dislikes complex rules and bureaucracy", "Potential for disruption to his established routines"],
    "attitude_technology": "Views technology as a practical tool to improve work efficiency or home comfort. Prefers straightforward, robust, and cost-effective solutions that are easy to use and maintain. Not interested in novelty for its own sake.",
    "attitude_energy": "Primarily driven by cost-effectiveness and reliability. Wants energy systems that are dependable, affordable, and don't require complicated management. Open to proven energy-saving measures if they offer clear financial returns and are simple to implement.",
    "motivation": "Ensuring a stable and comfortable life for his family, avoiding unnecessary hassle, practical problem-solving in his home and work."
  },
  {
    "name": "Hannah Nguyen",
    "age": 28,
    "occupation": "UX Designer",
    "location": "Berlin",
    "demographics": ["minimalist"],
    "values": ["Sustainability", "Ethical progress", "Social responsibility", "Innovation", "Minimalism"],
    "challenges": ["Pressure from rapid societal and technological change", "Concerned about global crises (climate change, social inequality)", "Ensuring technology is used ethically"],
    "attitude_technology": "Embraces technology, including AI tools, as a powerful force for positive change and efficiency. Values well-designed, intuitive, ethical, and sustainable tech. An early adopter who critically evaluates technology's broader impact.",
    "attitude_energy": "Highly values renewable and sustainable energy solutions. Actively seeks ways to minimize her personal energy footprint, support ethical energy providers, and optimize consumption through smart home technology. Prioritizes ecological impact.",
    "motivation": "Contributing to a more sustainable and equitable future, living in alignment with her personal values, promoting responsible innovation, reducing environmental impact."
  },
  {
    "name": "Felix König",
    "age": 55,
    "occupation": "IT Consultant",
    "location": "Munich",
    "demographics": ["tech-savvy", "self-employed"],
    "values": ["Efficiency", "Autonomy", "Smart investment", "Control", "Innovation", "Comfort"],
    "challenges": ["Staying ahead in a fast-paced technological landscape", "Managing complex integrated systems"],
    "attitude_technology": "Highly tech-savvy and an early adopter. Embraces automation and smart systems to optimize his personal and professional life. Sees technology as an enabler for efficiency, convenience, control, and intelligent investment. Enjoys integrating and managing complex tech stacks.",
    "attitude_energy": "Views energy consumption as something to be meticulously optimized and controlled through smart home and energy management systems. Invests in renewable energy (e.g., solar panels, home battery storage) for financial returns, increased energy independence, and maximizing efficiency.",
    "motivation": "Maximizing personal and financial efficiency, achieving energy self-reliance, leveraging cutting-edge technology for lifestyle and investment benefits, embracing innovation."
  },
  {
    "name": "David Müller",
    "age": 72,
    "occupation": "Retired Teacher",
    "location": "Rural Village",
    "demographics": ["widower", "lives alone"],
    "values": ["Simplicity", "Tradition", "Privacy", "Community (local)", "Reliability"],
    "challenges": ["Feeling overwhelmed by rapid technological change", "Concerns about data privacy and security", "Limited tech literacy and patience for new interfaces"],
    "attitude_technology": "Skeptical and resistant to new technology, especially if it feels intrusive or overly complex. Prefers manual processes and familiar tools. Uses essential tech (e.g., basic mobile phone) out of necessity but avoids smart devices or complex online services.",
    "attitude_energy": "Values traditional, reliable energy sources. Primarily concerned with stable and affordable heating and electricity. Not interested in smart energy solutions or renewables unless they are extremely simple, proven, and offer significant, risk-free cost savings with no digital complexity.",
    "motivation": "Maintaining a simple, private, and comfortable retirement, avoiding perceived risks and complexities of modern tech, preserving familiar routines."
  },
  {
    "name": "Lena Schmidt",
    "age": 21,
    "occupation": "University Student (Environmental Science)",
    "location": "University City",
    "demographics": ["lives in shared apartment", "activist"],
    "values": ["Climate justice", "Social equity", "Collective action", "Sustainability", "Innovation for good"],
    "challenges": ["Limited personal financial means", "Frustration with political inaction on climate change", "Anxiety about the future of the planet"],
    "attitude_technology": "Embraces technology for advocacy, information sharing, and organizing. Critically evaluates tech for its environmental and social impact. Interested in open-source, collaborative, and decentralized technologies that support sustainable practices and community building.",
    "attitude_energy": "Strong advocate for 100% renewable energy and energy efficiency. Actively seeks to reduce her personal energy consumption (e.g., public transport, minimalist living) and supports policies that promote large-scale sustainable energy transitions. May use apps to track impact.",
    "motivation": "Driving systemic change for climate justice and social equity, mobilizing communities, living a life consistent with her environmental values, securing a livable future."
  },
  {
    "name": "Mark Johnson",
    "age": 50,
    "occupation": "Small-scale Farmer",
    "location": "Rural Farmland",
    "demographics": ["runs family farm", "practical-minded"],
    "values": ["Self-reliance", "Durability", "Cost-effectiveness", "Practicality", "Connection to nature"],
    "challenges": ["Reliance on weather patterns", "Fluctuating market prices for produce", "Maintaining aging equipment", "Access to reliable infrastructure in rural areas"],
    "attitude_technology": "Sees technology as a means to improve farm productivity and resilience. Prefers robust, repairable, and field-tested equipment. Interested in basic automation (e.g., irrigation sensors) if it offers clear return on investment and reduces manual labor, but wary of overly complex or fragile systems.",
    "attitude_energy": "Energy is a significant operational cost. Seeks reliable, affordable, and robust energy solutions. May consider off-grid solar or wind for specific farm needs (e.g., water pumps, remote sheds) if it's cost-effective and dependable. Prioritizes fuel efficiency for machinery. Interest in energy independence for the farm.",
    "motivation": "Ensuring the long-term viability and profitability of his farm, maintaining his family's livelihood, reducing operational costs, adapting to environmental changes."
  },
  {
    "name": "Clara Weber",
    "age": 33,
    "occupation": "Marketing Director",
    "location": "Major City Apartment",
    "demographics": ["single", "high income", "busy lifestyle"],
    "values": ["Convenience", "Time-saving", "Comfort", "Personalization", "Modern living"],
    "challenges": ["Extremely busy schedule", "Information overload", "Finding time for self-care"],
    "attitude_technology": "Embraces technology that enhances convenience, saves time, and simplifies daily routines. A user of premium smart home devices, subscription services, and AI assistants. Values seamless integration and intuitive user experiences, willing to pay for cutting-edge solutions.",
    "attitude_energy": "Prefers 'set-and-forget' energy solutions that optimize comfort and efficiency without requiring active management. Will invest in smart thermostats, energy-efficient appliances, and potentially premium green energy plans if they offer convenience and align with a modern, responsible lifestyle, without being a hassle.",
    "motivation": "Maximizing personal time and comfort, maintaining a high-efficiency lifestyle, leveraging technology to manage a demanding career and personal life seamlessly."
  },
  {
    "name": "Ben Carter",
    "age": 42,
    "occupation": "Software Engineer (Open Source Specialist)",
    "location": "Mid-sized City",
    "demographics": ["privacy advocate", "frequent remote worker"],
    "values": ["Data privacy", "Transparency", "Open source", "Decentralization", "Security"],
    "challenges": ["Distrust of large corporations and government surveillance", "Finding truly private and secure tech alternatives", "Educating others about digital risks"],
    "attitude_technology": "Highly tech-savvy but deeply skeptical of proprietary software and data collection. Actively seeks out and contributes to open-source alternatives, custom builds, and privacy-focused solutions. Values control over his data and devices. Avoids cloud-dependent smart home tech.",
    "attitude_energy": "Concerned about the environmental impact of energy generation and the data implications of smart grids. Prefers locally-generated, transparently managed renewable energy solutions. May be interested in off-grid or community-owned energy projects. Focuses on minimal, efficient energy consumption for privacy and sustainability reasons.",
    "motivation": "Protecting digital rights and privacy, promoting ethical technology development, advocating for open and secure systems, fostering digital literacy."
  },
  {
    "name": "Sarah Chen",
    "age": 31,
    "occupation": "Caregiver (Part-time)",
    "location": "Urban Public Housing",
    "demographics": ["single parent", "low income"],
    "values": ["Survival", "Affordability", "Children's well-being", "Community support"],
    "challenges": ["Struggling to afford basic necessities", "High energy bills in inefficient housing", "Limited access to information or resources for improvement"],
    "attitude_technology": "Primarily views technology as a means to connect with essential services, family, and educational resources for her child. Cost is a major barrier to adoption. Seeks free or low-cost digital solutions; avoids anything that adds complexity or financial burden.",
    "attitude_energy": "Overwhelmingly driven by the need to minimize energy bills to meet basic needs. Energy efficiency measures are only considered if they are free, easily accessible, and provide immediate, tangible savings without upfront cost. Struggles with 'energy poverty' and makes difficult choices between heating, food, and other essentials.",
    "motivation": "Ensuring her child's basic needs are met, keeping living costs as low as possible, seeking stability and security amidst financial hardship."
  },
  {
    "name": "Thomas Keller",
    "age": 48,
    "occupation": "Automotive Engineer",
    "location": "Suburban Home with Workshop",
    "demographics": ["hobbyist", "DIY enthusiast"],
    "values": ["Innovation", "Problem-solving", "Understanding how things work", "Efficiency", "Hands-on experience"],
    "challenges": ["Finding time for his numerous projects", "Keeping up with new technical developments in his hobbies", "The initial cost of advanced components"],
    "attitude_technology": "Loves to tinker with technology, build custom solutions, and integrate various systems. Views technology as a sandbox for creativity and optimization. Enjoys understanding the underlying principles and isn't afraid of complex installations or programming. An early adopter of components rather than finished products.",
    "attitude_energy": "Fascinated by energy systems and efficiency. Enjoys designing and implementing his own smart energy solutions, like optimizing home solar panel output, building battery storage, or automating energy usage patterns. Motivation is as much about the challenge and learning as it is about savings or sustainability. Might convert a car to electric.",
    "motivation": "Personal intellectual stimulation, the satisfaction of building and optimizing, learning new skills, achieving a high degree of control and efficiency in his personal systems."
  }
]


try:
    import google.generativeai as genai
    GEMINI_IMPORTED = True
except ImportError:
    GEMINI_IMPORTED = False

st.set_page_config(
    page_title="Green Impact Wallet – GreenMatch",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def get_connection():
    conn = sqlite3.connect("greenmatch.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_state (
            user_id INTEGER PRIMARY KEY,
            profile_json TEXT,
            challenges_json TEXT,
            accepted_ids_json TEXT,
            completed_ids_json TEXT,
            tokens INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()


def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(email: str, name: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
        (email.lower().strip(), name.strip(), hash_pw(password)),
    )
    conn.commit()
    return cur.lastrowid


def get_user_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    return cur.fetchone()


def load_state(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_state WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        return None
    return {
        "profile": json.loads(row["profile_json"]) if row["profile_json"] else None,
        "challenges": json.loads(row["challenges_json"]) if row["challenges_json"] else [],
        "accepted_ids": set(json.loads(row["accepted_ids_json"])) if row["accepted_ids_json"] else set(),
        "completed_ids": set(json.loads(row["completed_ids_json"])) if row["completed_ids_json"] else set(),
        "tokens": row["tokens"] or 0,
    }


def save_state(user_id: int, profile, challenges, accepted_ids, completed_ids, tokens: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO user_state (user_id, profile_json, challenges_json,
                                accepted_ids_json, completed_ids_json, tokens)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            profile_json = excluded.profile_json,
            challenges_json = excluded.challenges_json,
            accepted_ids_json = excluded.accepted_ids_json,
            completed_ids_json = excluded.completed_ids_json,
            tokens = excluded.tokens
        """,
        (
            user_id,
            json.dumps(profile) if profile else None,
            json.dumps(challenges) if challenges else None,
            json.dumps(list(accepted_ids)) if accepted_ids is not None else None,
            json.dumps(list(completed_ids)) if completed_ids is not None else None,
            int(tokens),
        ),
    )
    conn.commit()



@st.cache_resource(show_spinner=False)
def get_gemini_model():
    if not GEMINI_IMPORTED:
        return None

    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-pro")


def _extract_json(text: str) -> Any:
    text = text.strip()
    if "```" in text:
        blocks = re.findall(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
        if blocks:
            text = blocks[0].strip()
    return json.loads(text)


def generate_challenges_with_gemini(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Ask Gemini to generate 3–4 personalised challenges, using the archetype personas
    as a mental model. The UI stays user-based, but the AI can think in terms of
    Julia / Kevin / Hannah / Felix etc. when shaping the content.
    """
    model = get_gemini_model()
    if model is None:
        return []

    system_prompt = """
You design personalised, realistic sustainability challenges.

You have access to a library of archetype personas (ARCHETYPE_PERSONAS below).
Each persona describes values, challenges, attitudes to technology & energy, and motivation.

Your task for each user_profile:

1. Internally decide which *one or two* archetype personas the user is closest to
   (based on age, values, tech attitude, income, housing, etc.).
2. Generate 3–4 challenges that:
   - are feasible for this specific user (respect housing, devices, financial situation,
     tech comfort, and anything they wrote about habits),
   - reflect the *tone and priorities* of the matched personas
     (e.g. Sarah → zero-cost basics, David → ultra simple & offline,
      Felix / Thomas → advanced smart home / DIY, Hannah / Lena → climate & ethics focus,
      Clara → convenience & automation, Mark → farm & self-reliance, Ben → privacy-aware solutions),
   - focus on realistic energy or CO₂ reduction and/or clear cost savings.

Important constraints and nuances:

- If the profile hints at low income / financial stress (e.g. similar to Sarah or Julia):
  - Avoid upfront investments and expensive devices.
  - Prefer free or very low-cost measures with immediate impact.
- If the profile looks tech-skeptical, older, or overwhelmed (e.g. David):
  - Keep actions simple, offline, and low-complexity.
  - Do not require new apps, complex dashboards, or cloud accounts.
- If the profile is tech-savvy or loves tinkering (e.g. Felix, Thomas, Ben):
  - You MAY propose smart-home automations, monitoring, or DIY projects,
    but they must still be concrete and realistically doable.
  - For Ben, explicitly avoid surveillance-heavy cloud solutions; prefer local / privacy-friendly options.
- For activist / climate-justice types (e.g. Lena, Hannah):
  - You can include one challenge that links personal behaviour with community / systemic impact.
- Always describe concrete behaviour: what to do, how often, for how long.
- For each challenge, give a rough monthly CO₂ saving as a *positive number* in kg.
  - Usually between 3 and 100 kg/month. Avoid 0 or unrealistically huge values.

Output format (VERY IMPORTANT):

Return ONLY valid JSON with exactly this structure:

{
  "challenges": [
    {
      "id": "short_unique_id",
      "title": "short title",
      "description": "1–3 short sentences explaining what to do.",
      "difficulty": "Easy | Medium | Advanced",
      "estimated_monthly_co2_saving_kg": number,
      "why_it_fits": "1–2 sentences explaining why this suits THIS user."
    }
  ]
}

- DO NOT include persona names in the JSON.
- DO NOT add extra explanation outside of the JSON.
"""

    prompt = (
        system_prompt
        + "\n\nARCHETYPE_PERSONAS:\n"
        + json.dumps(ARCHETYPE_PERSONAS, ensure_ascii=False)
        + "\n\nUser profile:\n"
        + json.dumps(profile, ensure_ascii=False)
    )

    try:
        resp = model.generate_content(prompt)
        data = _extract_json(resp.text)
        return data.get("challenges", [])
    except Exception as e:
        st.warning(f"Gemini error (using fallback challenges): {e}")
        return []


def analyze_image_with_gemini(image: Image.Image, challenge: Dict[str, Any]) -> str:
    model = get_gemini_model()
    if model is None:
        return "Gemini not configured – treat this as manual confirmation."

    prompt = f"""
You check if a photo could plausibly be evidence for a sustainability challenge.

Challenge:
Title: {challenge['title']}
Description: {challenge['description']}

Reply in 3–4 short sentences:
- Is the image plausibly related? Be generous, not strict.
- Mention one positive aspect.
- If something clearly doesn't fit, point it out gently.
No scores, just a friendly explanation.
"""

    try:
        resp = model.generate_content([prompt, image])
        return resp.text
    except Exception as e:
        return f"Error while calling Gemini: {e}"



def simple_fallback_challenges(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    motivations = " ".join(profile.get("motivations", [])).lower()
    devices = " ".join(profile.get("devices", [])).lower()
    housing = profile.get("housing", "apartment")

    challenges: List[Dict[str, Any]] = []

    challenges.append({
        "id": "heat_1c",
        "title": "Lower room temperature by 1°C",
        "description": "Keep your rooms about 1°C cooler than usual for the next 4 weeks.",
        "difficulty": "Easy",
        "estimated_monthly_co2_saving_kg": 20,
        "why_it_fits": "A small, low-effort adjustment that usually doesn’t reduce comfort."
    })

    challenges.append({
        "id": "standby",
        "title": "Turn off standby devices at night",
        "description": "Identify at least 5 devices and switch them fully off every night.",
        "difficulty": "Easy",
        "estimated_monthly_co2_saving_kg": 10,
        "why_it_fits": "Quick action with visible impact on both your bill and emissions."
    })

    if "car" in profile.get("habits", "").lower():
        challenges.append({
            "id": "car_free_day",
            "title": "Choose one car-free workday",
            "description": "Once per week, use public transport, bike or walk instead of driving.",
            "difficulty": "Medium",
            "estimated_monthly_co2_saving_kg": 25,
            "why_it_fits": "Targets your commuting pattern and also supports a healthier routine."
        })

    if "ev" in devices:
        challenges.append({
            "id": "night_charging",
            "title": "Charge your EV mainly at night",
            "description": "Schedule your EV charging to off-peak or high-renewable hours.",
            "difficulty": "Medium",
            "estimated_monthly_co2_saving_kg": 30,
            "why_it_fits": "You own an EV, so small changes in charging time can have a big effect."
        })

    if housing == "house":
        challenges.append({
            "id": "shower_shorter",
            "title": "Shorten hot showers",
            "description": "Reduce each shower by around 2 minutes and slightly lower the hot water temperature.",
            "difficulty": "Medium",
            "estimated_monthly_co2_saving_kg": 15,
            "why_it_fits": "Water heating is a major energy consumer in houses."
        })

    return challenges[:4]


init_db()

if "user" not in st.session_state:
    st.session_state.user = None        # row from users table
if "profile" not in st.session_state:
    st.session_state.profile = None
if "challenges" not in st.session_state:
    st.session_state.challenges = []
if "accepted_ids" not in st.session_state:
    st.session_state.accepted_ids = set()
if "completed_ids" not in st.session_state:
    st.session_state.completed_ids = set()
if "tokens" not in st.session_state:
    st.session_state.tokens = 0
if "state_loaded" not in st.session_state:
    st.session_state.state_loaded = False


def total_potential_co2() -> int:
    return sum(
        c.get("estimated_monthly_co2_saving_kg", 0)
        for c in st.session_state.challenges
        if c.get("id") in st.session_state.accepted_ids
    )


def level_from_tokens(tokens: int) -> str:
    if tokens >= 150:
        return "🌟 Planet Hero"
    if tokens >= 80:
        return "🚀 Impact Explorer"
    if tokens >= 30:
        return "✨ Eco Starter"
    return "🍃 Getting started"


st.markdown("## GreenMatch – your personal sustainability coach")

if st.session_state.user is None:
    login_tab, register_tab = st.tabs(["🔑 Login", "🆕 Register"])

    with login_tab:
        st.markdown("#### Welcome back")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            row = get_user_by_email(email)
            if row and row["password_hash"] == hash_pw(password):
                st.session_state.user = row
                st.session_state.state_loaded = False  # will trigger load below
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with register_tab:
        st.markdown("#### Create an account")
        r_email = st.text_input("Email ", key="r_email")
        r_name = st.text_input("Name", key="r_name")
        r_pw1 = st.text_input("Password  ", type="password", key="r_pw1")
        r_pw2 = st.text_input("Confirm password", type="password", key="r_pw2")

        if st.button("Register"):
            if not r_email or not r_pw1:
                st.warning("Please provide at least an email and password.")
            elif r_pw1 != r_pw2:
                st.warning("Passwords do not match.")
            elif get_user_by_email(r_email):
                st.warning("An account with this email already exists.")
            else:
                try:
                    user_id = create_user(r_email, r_name, r_pw1)
                    st.success("Account created. You can now log in.")
                except Exception as e:
                    st.error(f"Failed to create user: {e}")

    st.stop()

user = st.session_state.user

if not st.session_state.state_loaded:
    state = load_state(user["id"])
    if state:
        st.session_state.profile = state["profile"]
        st.session_state.challenges = state["challenges"]
        st.session_state.accepted_ids = state["accepted_ids"]
        st.session_state.completed_ids = state["completed_ids"]
        st.session_state.tokens = state["tokens"]
    st.session_state.state_loaded = True


top_left, top_right = st.columns([3, 1])

with top_left:
    st.markdown(f"### 👋 Hello, **{user['name'] or user['email']}**")

with top_right:
    tokens = st.session_state.tokens
    st.metric("Reward points", tokens)
    st.caption(level_from_tokens(tokens))

st.markdown("---")

st.sidebar.markdown(f"Logged in as **{user['email']}**")
if st.sidebar.button("Logout"):
    for key in ["user", "profile", "challenges", "accepted_ids", "completed_ids", "tokens", "state_loaded"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

left, right = st.columns([1.2, 1.8])

with left:
    st.markdown("### 👤 Your profile")

    profile = st.session_state.profile or {}

    with st.form("profile_form", clear_on_submit=False):
        name = st.text_input("Name", value=profile.get("name", user["name"] or ""))
        age = st.slider("Age", 16, 90, value=profile.get("age", 30))
        country = st.text_input("Country / region", value=profile.get("country", ""))

        housing = st.selectbox(
            "Living situation",
            ["apartment", "house", "other"],
            index=["apartment", "house", "other"].index(profile.get("housing", "apartment")),
        )

        st.markdown("**Devices you have**")
        device_options = [
            "Electric car (EV)",
            "Solar panels (PV)",
            "Heat pump",
            "Smart thermostat",
            "Smart meter",
        ]
        selected_devices = st.multiselect(
            "Select all that apply",
            device_options,
            default=[d for d in profile.get("devices", []) if d in device_options],
        )
        other_devices = st.text_input(
            "Other devices (comma separated)",
            value=", ".join([d for d in profile.get("devices", []) if d not in device_options]),
            placeholder="e.g. electric scooter, storage battery",
        )

        # motivations: multi + free text
        st.markdown("**What motivates you the most?**")
        motivation_options = ["Save money", "Protect climate", "More comfort", "Healthy lifestyle"]
        selected_motivations = st.multiselect(
            "Choose one or more",
            motivation_options,
            default=[m for m in profile.get("motivations", []) if m in motivation_options],
        )
        custom_motivation = st.text_input(
            "Add your own motivation (optional)",
            value=profile.get("custom_motivation", ""),
            placeholder="e.g. be a good role model for my kids",
        )

        habits = st.text_area(
            "Anything about your current habits? (optional)",
            value=profile.get("habits", ""),
            placeholder="e.g. I commute by car, work from home 3 days, like long showers…",
        )

        submitted = st.form_submit_button("✨ Generate / refresh my challenges")

    if submitted:
        all_devices = [d for d in selected_devices]
        if other_devices.strip():
            all_devices.extend([d.strip() for d in other_devices.split(",") if d.strip()])

        all_motivations = [m for m in selected_motivations]
        if custom_motivation.strip():
            all_motivations.append(custom_motivation.strip())

        profile = {
            "name": name.strip() or (user["name"] or "User"),
            "age": age,
            "country": country.strip(),
            "housing": housing,
            "devices": all_devices,
            "motivations": all_motivations,
            "custom_motivation": custom_motivation.strip(),
            "habits": habits,
        }

        st.session_state.profile = profile

        with st.spinner("Talking to AI to craft your personal challenges…"):
            challenges = generate_challenges_with_gemini(profile)
        if not challenges:
            challenges = simple_fallback_challenges(profile)

        st.session_state.challenges = challenges
        st.session_state.accepted_ids = set()
        st.session_state.completed_ids = set()
        st.session_state.tokens = st.session_state.tokens  # keep existing rewards

        save_state(user["id"], st.session_state.profile,
                   st.session_state.challenges,
                   st.session_state.accepted_ids,
                   st.session_state.completed_ids,
                   st.session_state.tokens)

        st.success("Your challenges have been updated on the right ✅")

    st.markdown("---")
    st.markdown("#### 🌍 Monthly potential")
    potential = total_potential_co2()
    st.metric("CO₂ you could save / month", f"{potential} kg")
    if potential == 0:
        st.caption("Accept at least one challenge to see your potential impact.")
    else:
        st.progress(min(1.0, potential / 100.0))


with right:
    st.markdown("### 🔮 Your personalised challenges")

    if not st.session_state.challenges:
        st.info("Fill out or update your profile on the left and click **Generate / refresh my challenges**.")
    else:
        for ch in st.session_state.challenges:
            cid = ch["id"]
            accepted = cid in st.session_state.accepted_ids
            completed = cid in st.session_state.completed_ids

            with st.container(border=True):
                header_cols = st.columns([3, 1])
                with header_cols[0]:
                    st.markdown(f"**{ch['title']}**")
                with header_cols[1]:
                    st.caption(ch.get("difficulty", ""))
                    st.caption(f"≈ {ch.get('estimated_monthly_co2_saving_kg', 0)} kg CO₂ / month")

                st.write(ch["description"])
                st.caption(f"Why this fits you: {ch['why_it_fits']}")

                btn_cols = st.columns(3)
                with btn_cols[0]:
                    if not accepted:
                        if st.button("Accept", key=f"accept_{cid}"):
                            st.session_state.accepted_ids.add(cid)
                            # small instant reward for accepting a challenge
                            st.session_state.tokens += 3
                    else:
                        st.success("Accepted")

                with btn_cols[1]:
                    if accepted and not completed:
                        if st.button("Mark completed", key=f"done_{cid}"):
                            st.session_state.completed_ids.add(cid)
                            # bigger reward on completion: based on CO2 impact
                            gain = max(5, ch.get("estimated_monthly_co2_saving_kg", 0) // 5)
                            st.session_state.tokens += gain
                    elif completed:
                        st.success("Completed ✔️")

                with btn_cols[2]:
                    with st.expander("Upload proof (optional)", expanded=False):
                        proof = st.file_uploader(
                            "Upload image",
                            key=f"proof_{cid}",
                            type=["png", "jpg", "jpeg"],
                            label_visibility="collapsed",
                        )
                        if st.button("Ask AI to check", key=f"check_{cid}"):
                            if proof is None:
                                st.warning("Please upload a photo first.")
                            else:
                                img = Image.open(proof)
                                with st.spinner("Checking with AI…"):
                                    result = analyze_image_with_gemini(img, ch)
                                st.markdown("**AI feedback:**")
                                st.write(result)

        st.markdown("---")
        accepted_count = len(st.session_state.accepted_ids)
        completed_count = len(st.session_state.completed_ids)
        st.caption(
            f"Accepted: {accepted_count} • Completed: {completed_count} • "
            f"Potential monthly CO₂ saving: {total_potential_co2()} kg • "
            f"Reward points: {st.session_state.tokens} ({level_from_tokens(st.session_state.tokens)})"
        )

# Persist state at the end of the run
save_state(
    user["id"],
    st.session_state.profile,
    st.session_state.challenges,
    st.session_state.accepted_ids,
    st.session_state.completed_ids,
    st.session_state.tokens,
)
