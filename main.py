import os
import json
import re
import sqlite3
import hashlib
from typing import Dict, Any, List

import streamlit as st
from PIL import Image



with open("persona_analysis.json", "r", encoding="utf-8") as f:
    ARCHETYPE_PERSONAS = json.load(f)

with open("companies.json", "r", encoding="utf-8") as f:
    COMPANY_LISTS = json.load(f)

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
        api_key = os.getenv("GEMINI_API_KEY")
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
You are a helpful AI assistant. You design personalised, realistic sustainability challenges.

You have access to a library of archetype personas (ARCHETYPE_PERSONAS) which describe values, challenges, and motivations. You also have access to a curated list of sustainable startups (COMPANY_LISTS).

Your task is to analyze the provided user_profile and perform the following steps:

1.  **Internal Persona Matching:** Silently determine which **one or two** archetype personas the user is closest to based on their age, values, tech attitude, income, housing, and habits.

2.  **Company-Driven Challenge Generation:** Generate 3–4 challenges that are **directly inspired by the products or services** in the `COMPANY_LISTS`.

Each challenge must:
*   Be linked to a specific company. The action you describe should be something a user could achieve using a product from the list. Mention the company by name as a concrete example (e.g., "...using a kit from YUMA or Priwatt," or "...by switching to WILDBAGS.").
*   Be feasible for the user. The suggested company and product must respect the user's housing situation, financial constraints, and comfort with technology.
*   Reflect the persona's priorities. The challenge's tone and goal must align with the values of the matched persona (e.g., cost-saving for Sarah, convenience for Clara, tech optimization for Felix).
*   Offer clear impact. Focus on realistic energy or CO₂ reduction and/or clear cost savings.

---
#### **Important Constraints and Nuances:**

*   **Financial Sensitivity (e.g., Sarah, Julia):** For users on a low income, **only** suggest challenges based on low-cost or free company offerings. For example, switching to WILDPLASTIC trash bags is a great fit; suggesting a Priwatt solar system (which requires a large upfront investment) is **not**.
*   **Tech Skepticism (e.g., David):** For users who are older, overwhelmed, or tech-averse, suggest simple, offline actions. A good match would be hosting bees with Wildbiene + Partner. A poor match would be setting up a smart EV charger from Entratek.
*   **Tech-Savvy & DIY (e.g., Felix, Thomas):** For these users, you **should** propose challenges that involve smart-home tech, data monitoring, or hands-on installation, such as the offerings from Priwatt, YUMA, or Entratek.
*   **Privacy-Aware (e.g., Ben):** When suggesting tech solutions for this persona, prioritize companies that offer local control or have a clear privacy focus.
*   **Activist & Ethical Focus (e.g., Lena, Hannah):** For these users, highlight the systemic or community impact of a company's mission. WILDPLASTIC (fair wages for collectors) or Wildbiene + Partner (supporting agricultural pollination) are excellent examples.
*   **Concrete Actions:** Always describe a specific behavior: what to do, how often, for how long.
*   **CO₂ Savings:** For each challenge, provide a rough monthly CO₂ saving as a *positive number* in kg (typically between 3 and 100 kg/month).

---
#### **Example of a Good Response Flow:**

*   **User Profile:** "I'm 45, own my home with a garden, and recently bought an electric car. I'm a software engineer, so I'm comfortable with tech and like optimizing things to save money and be more efficient."
*   **Internal Persona Match:** Felix (tech-savvy, data-driven) and Thomas (DIY, homeowner).
*   **Company Match from List:** Entratek GmbH (specializes in EV charging solutions).
*   **Generated Challenge:**
    *   **Title:** "Install an Intelligent EV Charging Station"
    *   **Description:** "Optimize your electric vehicle charging by installing a smart wallbox from a provider like Entratek. This allows you to schedule charging for off-peak hours and monitor your energy consumption."
    *   **Why_it_fits:** "As a tech-savvy homeowner with an EV, this project aligns perfectly with your interest in optimization and efficiency, giving you direct control over your energy costs."

---
#### **Output Format (VERY IMPORTANT):**

Return ONLY valid JSON with exactly this structure. Do not add any text or explanation outside of the JSON block.

```json
{
  "challenges": [
    {
      "id": "short_unique_id",
      "title": "short title",
      "description": "1–3 short sentences explaining what to do, referencing a company from the list.",
      "difficulty": "Easy | Medium | Advanced",
      "estimated_monthly_co2_saving_kg": number,
      "why_it_fits": "1–2 sentences explaining why this challenge and the suggested company's approach suit THIS user."
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
        + "\n\nCOMPANY_LISTS:\n"
        + json.dumps(COMPANY_LISTS, ensure_ascii=False)
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
