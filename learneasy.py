import streamlit as st

st.set_page_config(page_title="ILEARN-UGANDA", page_icon="📚")

st.title("📚 ILEARN-UGANDA")
st.write("Welcome, Learner!")

# DASHBOARD
menu = st.sidebar.selectbox("Go to", ["Dashboard", "Learning Outcomes", "Take Quiz", "My Progress"])

if menu == "Dashboard":
    st.header("Dashboard")
    st.button("📚 Learning Outcomes - MAIN")
    st.button("✏️ Take Quiz")
    st.button("📊 My Progress")

elif menu == "Learning Outcomes":
    st.header("Learning Outcomes")
    st.write("Choose Your Class")
    class_level = st.selectbox("Class", ["P1", "P2", "P3", "P4", "P5", "P6", "P7"])
    subject = st.selectbox("Subject", ["MAT", "ENG", "SST", "SCI", "CRE", "IRE", "KIS"])
    term = st.selectbox("Term", [1, 2, 3])
    st.success(f"You selected: {class_level} - {subject} - Term {term}")
    st.write("Outcomes will show here from your P4-P7 file.")

elif menu == "Take Quiz":
    st.header("✏️ Take Quiz")
    st.write("Choose Subject and Term to start quiz")

elif menu == "My Progress":
    st.header("📊 My Progress")
    st.progress(50)
    st.write("You have completed 50%")
