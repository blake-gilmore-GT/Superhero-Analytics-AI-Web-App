import google.generativeai as genai
import streamlit as st
import requests
import json
from hero_dict import superDict

gemini_API = st.secrets["GEMINI_API_KEY"]
api_token = st.secrets["SUPERHERO_API_TOKEN"]

genai.configure(api_key=gemini_API)
model = genai.GenerativeModel("models/gemini-2.5-flash")

st.title("My Superhero")

user_description = st.text_area("Describe the hero you're imagining:")
closest_matches = st.selectbox("How many closest hero matches should the LLM find?", [1, 2, 3, 5, 10])


def normalize(name):
    return name.lower().replace("-", "").replace(" ", "").strip()


if st.button("Find My Hero Match!"):
    placeholder = st.empty()
    with placeholder.container():
        st.write("Analyzing your response...")

    ai_prompt = f"""
    You are an expert superhero analyst. Based ONLY on the user's description below,
    estimate realistic superhero powerstats (0–100) and suggest {closest_matches} existing superhero names from the API
    that best match this description. Make sure every name given exactly matches a key in: {superDict}.

    Description:
    "{user_description}"

    Return ONLY a JSON object with two keys:
    1. stats: a dictionary with keys intelligence, strength, speed, durability, power, combat
    2. matches: a list of {closest_matches} superhero names (strings)
    """

    ai_response = model.generate_content(ai_prompt)
    st.write("AI Interpretation of Your Hero:")

    try:
        cleaned = ai_response.text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").replace("json", "", 1).strip()

        hero_json = json.loads(cleaned)
        hero_stats = hero_json["stats"]
        ai_matches = hero_json["matches"]

    except Exception as e:
        st.error("Failed to parse AI response as JSON.")
        st.write("Raw AI output:")
        st.code(ai_response.text)
        st.write("Error:", str(e))
        hero_stats = None
        ai_matches = []

    if hero_stats:
        placeholder.empty()
        st.json(hero_stats)

    if ai_matches:
        st.write("Fetching suggested heroes from the API...")

        normalized_ai_matches = [normalize(n) for n in ai_matches]
        indexList = []

        for heroInd in ai_matches:
            if heroInd in superDict:
                indexList.append(superDict[heroInd])

        every_hero = []
        for i in indexList:
            url = f"[https://superheroapi.com/api/](https://superheroapi.com/api/){api_token}/{i}"
            response = requests.get(url)
            data = response.json()

            if data.get("response") != "success":
                continue

            api_name = data.get("name", "")
            if normalize(api_name) in normalized_ai_matches:
                powerstats = data.get("powerstats", {})
                if not isinstance(powerstats, dict):
                    powerstats = {}

                stats = {
                    ability: int(power) if str(power).isdigit() else 0
                    for ability, power in powerstats.items()
                }
                every_hero.append({"name": api_name, "stats": stats})

        def difference_score(ai_hero, api_hero):
            if not isinstance(ai_hero, dict) or not isinstance(api_hero, dict):
                return 0
            return sum(abs(ai_hero.get(ability, 0) - api_hero.get(ability, 0)) for ability in ai_hero)

        for hero in every_hero:
            hero["score"] = difference_score(hero_stats, hero["stats"]) if hero_stats else 0

        top_matches = sorted(every_hero, key=lambda h: h["score"])[:closest_matches]

        st.subheader(f"Top {closest_matches} Closest Hero Matches:")
        for idx, match in enumerate(top_matches, start=1):
            st.write(f"{idx}. {match['name']} — Difference Score: {match['score']}")

        top_hero_names = [match["name"] for match in top_matches]
        top_hero_stats = [match["stats"] for match in top_matches]

        if top_hero_names:
            explanation_prompt = f"""
            You are an expert superhero analyst. Compare the following AI-generated hero to these top {closest_matches} superhero matches from the API.

            AI Hero Stats: {hero_stats}
            Top Matches:
            """
            for name, stats in zip(top_hero_names, top_hero_stats):
                explanation_prompt += f"\n{name}: {stats}"

            explanation_prompt += "\n\nProvide a narrative explanation highlighting similarities, differences, and strengths. Return it as readable text."

            explanation_response = model.generate_content(explanation_prompt)
            st.subheader("Gemini Analysis of Top Matches:")
            st.write(explanation_response.text)
        else:
            st.error("No hero matches were found in the API due to name mismatches.")
