import streamlit as st
import requests
import pandas as pd
import plotly.express as px

api_token = st.secrets["SUPERHERO_API_TOKEN"]

st.title("Super Stats Comparison :balance_scale:")

hero_name = st.text_input("Enter a superhero name to compare:", "Batman")

if hero_name:
    url = f"https://superheroapi.com/api/{api_token}/search/{hero_name}"
    response = requests.get(url)
    data = response.json()

    if data.get("response") == "success":
        hero = data["results"][0]
        stats = {k: int(v) if v != "null" else 0 for k, v in hero["powerstats"].items()}

        st.subheader(f"Hero: {hero['name']}")
        st.write("**Power Stats**")
        for stat, value in stats.items():
            st.write(f"**{stat.capitalize()}:** {value}")

        st.header("Enter Your Stats!")
        your_stats = {
            "intelligence": st.slider("**Intelligence**", 0, 100, 50),
            "strength": st.slider("**Strength**", 0, 100, 50),
            "speed": st.slider("**Speed**", 0, 100, 50),
            "durability": st.slider("**Durability**", 0, 100, 50),
            "power": st.slider("**Power**", 0, 100, 50),
            "combat": st.slider("**Combat**", 0, 100, 50)
        }

        if st.button(f"Compare with {hero['name']}"):
            st.subheader("Comparison Results")
            difference = 0
            for stat in your_stats:
                diff = abs(stats[stat] - your_stats[stat])
                difference += diff
                st.write(f"{stat.capitalize()}: Your {your_stats[stat]} vs {hero['name']} {stats[stat]} (Diff: {diff})")

            correlation = max(0, 100 - difference / 6)
            st.success(f"Correlation Score: {correlation:.2f}%")

            df = pd.DataFrame({
                "Stat": list(your_stats.keys()),
                "You": list(your_stats.values()),
                hero["name"]: list(stats.values())
            })

            fig = px.bar(
                df,
                x="Stat",
                y=["You", hero["name"]],
                barmode="group",
                title=f"Hero Stat Comparison with {hero['name']}",
                text_auto=True
            )
            st.plotly_chart(fig)

    else:
        st.error("Hero not found. Please try another hero name.")
