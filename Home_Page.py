import streamlit as st

# Title of App
st.title("Web Development Lab03")

# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Team 16, Web Development - Section E")
st.subheader("Blake Gilmore, Martin Sarmiento")


# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

superPhoto = "Images/hd-superhero.jpg"

st.image(superPhoto, width=800)

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1. Compare Yourself: A tool to see how you stack up against your favorite superhero!
2. My Superhero: A tool to find which superhero is YOUR hero! Enter what characteristics you want your superhero to have, and we'll match you to a superhero!
3. SuperBot: AI Chatbot here to answer any superhero questions you might have!

""")

