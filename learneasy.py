import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="LearnEasy", layout="centered")

CSV_FILE = "results.csv"

def load_results():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            return df.to_dict("records")
        except:
            return []
    return []

def save_results(results):
    df = pd.DataFrame(results)
    df.to_csv(CSV_FILE, index=False)

if "results" not in st.session_state:
    st.session_state.results = load_results()
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "last_submit_key" not in st.session_state:
    st.session_state.last_submit_key = ""

questions = [
    ("Q1. [English] What gets wetter the more it dries?", ["Water", "A towel", "A stone", "A cup"], "A towel", "A towel gets wetter as it dries you."),
    ("Q2. [Maths] The temperature of the room in the morning was 54 degrees Celsius. Find the temperature in degrees Fahrenheit.", ["129.2F", "120F", "54F", "100F"], "129.2F", "F = (C x 9/5) + 32 = (54 x 9/5) + 32 = 129.2F"),
    ("Q3. [CRE] How did the people of Israel survive in the wilderness while moving to the promised land?", ["God provided manna and quails", "They bought food", "They hunted", "They farmed"], "God provided manna and quails", "God provided manna and quails in the wilderness."),
    ("Q4. [SST] What is the largest vegetation in Uganda?", ["Tropical rainforest", "Montane forest", "Swamp vegetation", "Savanna"], "Tropical rainforest", "Tropical rainforest is the largest vegetation in Uganda."),
    ("Q5. [Maths] Simplify: -5 - (-6)", ["-11", "1", "11", "-1"], "1", "-5 + 6 = 1. Minus a minus becomes plus."),
    ("Q6. [Maths] A pair of packets of biscuits costs Sh. 1000. Find the cost of 7 similar packets of biscuits.", ["Sh. 3500", "Sh. 7000", "Sh. 500", "Sh. 14000"], "Sh. 3500", "One packet = 1000/2 = 500. 7 x 500 = 3500."),
    ("Q7. [Maths] How far can a fox run into a circular forest?", ["All the way through", "Quarter way", "Halfway", "To the centre"], "Halfway", "After halfway, it starts running out of the forest."),
    ("Q8. [Science] How does a mosquito differ from a cockroach in terms of their lifecycle?", ["Mosquito undergoes complete metamorphosis, cockroach undergoes incomplete metamorphosis", "Both undergo complete metamorphosis", "Both undergo incomplete metamorphosis", "Mosquito undergoes incomplete, cockroach undergoes complete"], "Mosquito undergoes complete metamorphosis, cockroach undergoes incomplete metamorphosis", "Mosquito has complete metamorphosis, cockroach has incomplete metamorphosis."),
    ("Q9. [Science] Why does heat travel faster in a solid than in a gas?", ["Particles in a solid are closer together", "Particles in a gas are closer together", "Solids are heavier", "Gases are colder"], "Particles in a solid are closer together", "Particles in a solid are closer together so heat passes faster."),
    ("Q10. [RE] How does the school prayer assist a learner?", ["It makes the learner sleep", "It helps the learner start the day with God", "It makes the learner late", "It makes the learner hungry"], "It helps the learner start the day with God", "School prayer helps the learner start the day with God."),
    ("Q11. [Maths] Simplify 2m - 8m + 13m", ["5m", "23m", "7m", "3m"], "7m", "2m - 8m = -6m, -6m + 13m = 7m."),
    ("Q12. [SST] Which country does Uganda border in the East?", ["Tanzania", "South Sudan", "DR Congo", "Kenya"], "Kenya", "Uganda borders Kenya in the East."),
    ("Q13. [Science] Why is heat unable to travel in a vacuum?", ["There are no particles to carry it", "Vacuum is too hot", "Vacuum is too cold", "Vacuum has many particles"], "There are no particles to carry it", "Vacuum is too hot to carry heat."),
    ("Q14. [Maths] Which of these is the net of a cylinder?", ["One circle and a triangle", "Two circles and a rectangle", "One circle and a square", "Three circles"], "Two circles and a rectangle", "A cylinder net has two circles and a rectangle."),
    ("Q15. [SST] Name the major physical feature that is known for the formation of relief rainfall in Eastern Uganda.", ["Mount Elgon", "Lake Victoria", "River Nile", "Rwenzori Mountains"], "Mount Elgon", "Mount Elgon causes relief rainfall in Eastern Uganda."),
    ("Q16. [English] Use the correct form: Sarah ........ meat to chicken. (Prefers, likes)", ["Likes", "Prefer", "Prefers", "Like"], "Prefers", "Sarah prefers meat to chicken."),
    ("Q17. [Maths] Molly is twice as old as Jolly. If the sum of their ages is 30, how old is Molly?", ["20 years", "10 years", "15 years", "30 years"], "20 years", "Jolly = 10, Molly = 20, total = 30."),
    ("Q18. [SST] What is a landlocked country?", ["A country with many lakes", "A country with no sea coast", "A country with many rivers", "A country with a big ocean"], "A country with no sea coast", "A landlocked country has no sea coast."),
    ("Q19. [CRE] 'I AM WHO I AM.' To whom was the statement made?", ["Abraham", "Jacob", "Moses", "David"], "Moses", "God said 'I AM WHO I AM' to Moses."),
    ("Q20. [English] One of the following words means elephant in Kiswahili.", ["Tendo", "Rembo", "Pembo", "Tembo"], "Tembo", "Tembo means elephant in Kiswahili."),
]

page = st.sidebar.selectbox("Go to", ["Take Quiz", "Teacher Dashboard"])

if page == "Take Quiz":
    st.title("LearnEasy Quiz")
    st.write("Answer all questions, then click Submit.")
    if st.button("Next Child - Clear for New Learner"):
        saved = st.session_state.get("results", [])
        st.session_state.clear()
        st.session_state.results = saved
        st.session_state.submitted = False
        st.session_state.last_submit_key = ""
        st.rerun()
    name = st.text_input("Your Name", key="name")
    school = st.text_input("Your School", key="school")
    answers = []
    for i, (q, options, correct, explain) in enumerate(questions):
        ans = st.radio(q, options, key=f"q{i}", index=None)
        answers.append(ans)
    if st.session_state.submitted:
        st.info("This child has already submitted. Click 'Next Child' above for the next learner.")
    if st.button("Submit Quiz - See My Results"):
        if st.session_state.submitted:
            st.warning("Already submitted. Click 'Next Child' for the next learner.")
        elif not name or not school:
            st.warning("Please enter Your Name and Your School first.")
        elif any(a is None for a in answers):
            st.warning("Please answer all questions before submitting.")
        else:
            submit_key = f"{name}|{school}|{answers}"
            if submit_key == st.session_state.last_submit_key:
                st.warning("Already submitted. Click 'Next Child' for the next learner.")
            else:
                score = 0
                for i, (q, options, correct, explain) in enumerate(questions):
                    if str(answers[i]) == str(correct):
                        score = score + 1
                total = len(questions)
                pct = round(score * 100 / total, 1)
                if pct >= 80:
                    grade = "A"
                    comment = "Excellent! Keep it up."
                elif pct >= 60:
                    grade = "B"
                    comment = "Very good!"
                elif pct >= 40:
                    grade = "C"
                    comment = "Good, keep practising."
                else:
                    grade = "D"
                    comment = "Keep trying, you can do better."
                new_row = {"Name": name, "School": school, "Score": f"{score}/{total}", "Percentage": pct, "Grade": grade, "Comment": comment}
                st.session_state.results.append(new_row)
                save_results(st.session_state.results)
                st.session_state.last_submit_key = submit_key
                st.session_state.submitted = True
                st.success(f"Well done {name}! You scored {score}/{total} = {pct}% Grade {grade}")
                st.write(comment)
                st.subheader("Review Your Answers")
                for i, (q, options, correct, explain) in enumerate(questions):
                    st.write(f"Q{i+1}: {q}")
                    st.write(f"Your answer: {answers[i]}")
                    st.write(f"Correct answer: {correct}")
                    if str(answers[i]) == str(correct):
                        st.write("Correct! Well done.")
                    else:
                        st.write("Not correct.")
                    st.write(f"Explanation: {explain}")
                    st.write("---")

if page == "Teacher Dashboard":
    st.title("Teacher Dashboard")
    results = st.session_state.get("results", [])
    st.write(f"Total attempts: {len(results)}")
    if st.button("Clear All Results - Start Fresh"):
        st.session_state.results = []
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        st.session_state.submitted = False
        st.session_state.last_submit_key = ""
        st.rerun()
    if len(results) == 0:
        st.info("No results yet. Let a child take the quiz first.")
    else:
        df = pd.DataFrame(results)
        df = df.sort_values(by="Percentage", ascending=False)
        st.subheader("Top 25 Learners")
        st.dataframe(df.head(25))
        st.subheader("All Results")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results CSV", csv, "learneasy_results.csv", "text/csv")
