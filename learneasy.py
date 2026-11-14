import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="LearnEasy", layout="wide")

RESULTS_FILE = "learneasy_results.csv"

if "results" not in st.session_state:
    if os.path.exists(RESULTS_FILE):
        try:
            st.session_state.results = pd.read_csv(RESULTS_FILE).to_dict("records")
        except:
            st.session_state.results = []
    else:
        st.session_state.results = []

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "last_score" not in st.session_state:
    st.session_state.last_score = 0
if "last_percentage" not in st.session_state:
    st.session_state.last_percentage = 0
if "last_grade" not in st.session_state:
    st.session_state.last_grade = ""
if "last_answers" not in st.session_state:
    st.session_state.last_answers = []
if "last_name" not in st.session_state:
    st.session_state.last_name = ""

def save_results():
    try:
        pd.DataFrame(st.session_state.results).to_csv(RESULTS_FILE, index=False)
    except:
        pass

page = st.sidebar.radio("Go to:", ["Take Quiz", "Teacher Dashboard"])

learning_outcomes = {
    "P5-M-T1-01 Sets": ["Describe, list and form sets","Identify types of sets - equal, equivalent, empty, subset","Find union and intersection of sets","Represent sets on Venn diagrams","Find probability of a coin, dice, days of week"],
    "P5-M-T1-02 Whole Numbers": ["Form numbers up to 999,999 from digits","State place value and value of digits","Expand numbers using place values and powers of 10","Write numbers in words and figures","Round off whole numbers to nearest 10, 100, 1000","Write Roman numerals up to 300"],
    "P5-M-T1-03 Number Patterns & Sequences": ["Identify even, odd, prime, square, cube numbers","Find multiples, LCM and HCF","Find prime factors by factor tree / ladder","Find increasing and decreasing sequences"],
    "P5-M-T1-04 Fractions": ["Identify numerator and denominator","Form equivalent fractions and simplify","Compare and order fractions","Convert improper to mixed numbers and vice versa","Add, subtract, multiply and divide fractions","Solve word problems on fractions"],
    "P5-M-T2-05 Decimals": ["Read, write and compare decimals","Convert fractions to decimals and vice versa","Add, subtract, multiply and divide decimals","Round decimals","Solve word problems on decimals"],
    "P5-M-T2-06 Percentages, Ratio & Proportion": ["Express a number as a percentage","Convert fractions and decimals to percentages","Find percentage of a quantity","Share in a given ratio","Solve word problems on percentages and ratio"],
    "P5-M-T2-07 Integers": ["Identify positive and negative integers","Represent integers on a number line","Compare and order integers","Add and subtract integers"],
    "P5-M-T2-08 Data Handling": ["Collect and record data in tables","Draw and interpret pictographs and bar graphs","Find mode, median, mean","Solve problems from graphs"],
    "P5-M-T3-09 Money": ["Identify Uganda currency notes and coins","Add, subtract, multiply and divide money","Find profit, loss, cost price and selling price","Solve word problems on money"],
    "P5-M-T3-10 Lines, Angles & Geometric Figures": ["Identify parallel, perpendicular and intersecting lines","Identify acute, right, obtuse, reflex angles","Identify properties of 2D and 3D shapes","Draw nets of solids"],
    "P5-M-T3-11 Time": ["Tell time on 12-hour and 24-hour clock","Convert time units","Find duration / time taken","Solve word problems on time"],
    "P5-M-T3-12 Measurement": ["Measure length, mass and capacity","Convert units - km-m-cm, kg-g, litres-ml","Find perimeter and area of squares and rectangles","Find volume of cubes and cuboids","Solve word problems on measurement"],
    "P5-SCI-T1-01 Keeping Poultry": ["Name types of poultry","Describe external parts of poultry","Explain feeding, housing, disease prevention","Keep farm records"],
    "P5-SCI-T1-02 Bee Keeping": ["Identify parts of a bee hive","Explain importance of bees","Describe products - honey, wax","State safety in bee keeping"],
    "P5-SCI-T1-03 Digestive System": ["Name parts of digestive system","Explain function of each part","State disorders and prevention","Explain balanced diet"],
    "P5-SCI-T1-04 Plants": ["Identify parts of a plant","Explain photosynthesis","State gas plants use - carbon dioxide","Explain uses of plants"],
    "P5-SCI-T2-05 Respiratory & Circulatory System": ["Name organs of breathing and blood circulation","Explain breathing","State diseases and prevention"],
    "P5-SCI-T2-06 Heat & Energy": ["Define heat","State sources of heat","Explain why heat cannot travel in a vacuum","Explain effects of heat"],
    "P5-SCI-T2-07 Light & Sound": ["State sources of light and sound","Explain reflection","State uses and dangers"],
    "P5-SCI-T2-08 Matter & Materials": ["Identify states of matter","Explain melting, evaporation, condensation","Identify materials and uses"],
    "P5-SCI-T3-09 Changes in Environment": ["Identify chemical, physical, biological changes","Give examples of changes","Explain causes and prevention of environmental damage"],
    "P5-SCI-T3-10 Keeping Goats & Sheep": ["State reasons for keeping goats/sheep","Name breeds - Mubende goats","Explain feeding, housing, diseases - pneumonia, foot rot"],
    "P5-SCI-T3-11 Keeping Cattle & Pigs": ["State reasons for keeping cattle/pigs","Explain breeds, feeding, housing, diseases"],
    "P5-SCI-T3-12 Sanitation & Health": ["Explain personal hygiene","State causes of common diseases","Explain prevention - clean water, latrines"],
    "P5-E-T1-01 Vehicle Repair": ["Use vocabulary - engine, tyre, steering, windscreen, seat belt","Construct sentences about vehicle parts","Read passage and answer questions"],
    "P5-E-T1-02 Print Media": ["Use vocabulary - advertisement, reporter, article, column","Read advertisement","Write advertisement"],
    "P5-E-T1-03 Travelling": ["Use vocabulary - journey, fare, ticket, luggage","Use Past Simple and Past Continuous","Write guided composition on a journey"],
    "P5-E-T2-04 Letter Writing": ["Write friendly and formal letters","Use correct format - address, date, salutation, body, closing","Use Future Simple Tense"],
    "P5-E-T2-05 Communication": ["Use vocabulary - post office, telephone, internet, email","Write dialogue","Use structures for asking and giving information"],
    "P5-E-T3-06 Culture": ["Use vocabulary - nationality, language","Talk about nationalities - Ugandan, Kenyan, Tanzanian","Read text on culture"],
    "P5-E-T3-07 Peace & Security": ["Use vocabulary - peace, security, soldier, police","Construct sentences","Read passage on peace"],
    "P5-E-T3-08 Services - Banks": ["Use vocabulary - bank, account, deposit, withdraw","Fill bank forms","Write sentences on banking"],
    "P5-E-ALL-09 Grammar & Punctuation": ["Use capital letters, full stop, question mark, apostrophe","Identify nouns, pronouns, verbs, adjectives, adverbs, prepositions, conjunctions","Use tenses correctly","Use synonyms and antonyms"],
    "P5-SST-T1-01 Location of Uganda": ["Locate Uganda on map of East Africa","Name neighbours - Kenya, Tanzania, Rwanda, DRC, South Sudan","State Uganda is landlocked","Use compass directions"],
    "P5-SST-T1-02 Physical Features": ["Identify mountains, lakes, rivers, rift valley","Explain formation of mountains","State uses of lakes and rivers"],
    "P5-SST-T1-03 Climate of Uganda": ["Define climate","Identify factors - altitude, latitude, vegetation","Identify climatic regions","Explain relief rainfall in Eastern Uganda - Mt Elgon"],
    "P5-SST-T1-04 Vegetation & Natural Resources": ["Identify vegetation types","Name resources - land, water, minerals, animals","State uses and conservation"],
    "P5-SST-T2-05 People of Pre-colonial Uganda": ["Identify ethnic groups - Bantu, Nilotics, Nilo-Hamites, Sudanic","Explain migration","Describe settlement patterns and organisation"],
    "P5-SST-T2-06 Foreign Influence": ["Identify explorers, traders, missionaries","State effects of foreign influence","Explain coming of Arabs 1844"],
    "P5-SST-T2-07 Population": ["Define population","State factors affecting population","Explain population distribution"],
    "P5-SST-T3-08 Uganda as Independent Nation": ["State independence 9th Oct 1962","Identify national symbols - flag, anthem, coat of arms","Explain meaning of colours"],
    "P5-SST-T3-09 Democracy & Citizenship": ["Define democracy, citizenship","Identify organs of government","Explain elections, ballot paper, constituency"],
    "P5-SST-T3-10 Economic Activities": ["Identify farming, fishing, mining, trade","Explain interdependence","State importance of transport"],
    "P5-RE-T1-01 Faith": ["Define faith - believing in God with full confidence","Name people of great faith - Abraham, Moses","Explain how faith overcomes problems"],
    "P5-RE-T1-02 Christianity & Islam": ["State facts about Islam and Christianity","Explain history of Islam in Uganda - Arab traders 1844","Show respect for other faiths"],
    "P5-RE-T1-03 Gods Word - The Bible": ["Name books of Bible","Explain how to read and study Bible","State uses of Bible"],
    "P5-RE-T1-04 Gods Word - Jesus": ["Describe life of Jesus as a child","Explain events of Holy Week","State importance of Holy Week"],
    "P5-RE-T2-05 Holy Spirit": ["Explain why Jesus promised Holy Spirit","State fruits and gifts of Holy Spirit","Identify symbols of Holy Spirit"],
    "P5-RE-T2-06 We Are The Church": ["Define Church","Explain work of Church","State roles in Church"],
    "P5-RE-T3-07 Witness": ["Define witness","Explain how to witness","Give examples of witnesses"],
    "P5-RE-T3-08 Christian Living": ["State Gods promises","Explain how to live as a Christian","Show love, forgiveness, service"],
    "P5-RE-IRE-01 Tawhid & Pillars": ["Define Tawhid","Recite Surat Al-Zilzala","State pillars of Islam - Shahada, Swallah, Zakat, Saum, Hajj"],
    "P5-RE-IRE-02 Fiqh & Fasting": ["Explain fasting in Ramadhan","State rules of prayer","Explain Day of Judgement"],
    "P5-RE-IRE-03 History of Islam": ["Describe Prophet Muhammad at Medina","State history of Islam in Uganda"],
    "P5-KIS-T1-01 Maamkuzi na Maagano": ["Kusalimia - Shikamoo, Habari za asubuhi","Kuagana - Safari njema, Lala salama","Kutumia maamkuzi katika mazungumzo"],
    "P5-KIS-T1-02 Familia na Nyumbani": ["Kutaja wanafamilia - baba, mama, kaka, dada","Kueleza kazi za nyumbani","Kuandika sentensi kuhusu familia"],
    "P5-KIS-T1-03 Shuleni": ["Kutaja vitu vya shule","Kueleza ratiba ya shule","Kusoma kifungu kuhusu shule"],
    "P5-KIS-T1-04 Mapishi / Chakula": ["Kutaja vyakula na viungo","Kueleza njia za kupika","Kusoma kwa ufahamu kuhusu mapishi"],
    "P5-KIS-T2-05 Wanyama": ["Kutaja wanyama - mbwa, paka, ngombe, mbuzi, simba","Kueleza makazi na chakula cha wanyama","Kutaja Kiswahili cha wanyama"],
    "P5-KIS-T2-06 Sarufi - Nomino": ["Kutambua nomino za pekee na za kawaida","Kutambua nomino za wingi na umoja","Kutunga sentensi na nomino"],
    "P5-KIS-T2-07 Sarufi - Vitenzi na Vivumishi": ["Kutambua vitenzi","Kutumia vitenzi katika sentensi","Kutambua vivumishi"],
    "P5-KIS-T2-08 Kusoma na Kuandika": ["Kusoma kifungu na kujibu maswali","Kuandika insha ya wasifu na masimulizi","Kuandika baruapepe na barua"],
    "P5-KIS-T3-09 Huduma ya Kwanza na Afya": ["Kutaja vifaa vya huduma ya kwanza","Kueleza umuhimu wa usafi","Kutumia msamiati wa afya"],
    "P5-KIS-T3-10 Methali na Semi": ["Kueleza maana ya methali","Kutumia methali katika mazungumzo","Kukariri vitanzandimi"],
}

questions = [
    ("Q1. [English] What gets wetter the more it dries?", ["Water", "A towel", "A stone", "A cup"], "A towel", "A towel gets wetter the more it dries you or dishes. It is a riddle!"),
    ("Q2. [Maths] The temperature of the room in the morning was 54 degrees Celsius. Find the temperature in degrees Fahrenheit.", ["54 F", "86 F", "129.2 F", "97.2 F"], "129.2 F", "Use F = (C x 9/5) + 32. So (54 x 9/5) + 32 = 97.2 + 32 = 129.2 F."),
    ("Q3. [CRE] How did the people of Israel survive in the wilderness while moving to the promised land?", ["God provided them with manna, quails and water", "They bought food from shops", "They grew crops in the desert", "They hunted animals only"], "God provided them with manna, quails and water", "God gave them manna in the morning, quails for meat in the evening, and water from the rock."),
    ("Q4. [SST] What is the largest vegetation in Uganda?", ["Tropical rainforest", "Montane forest", "Swamp vegetation", "Savanna grassland"], "Savanna grassland", "Savanna grassland covers the biggest part of Uganda. Rainforest is only in small areas like Mabira and Bwindi."),
    ("Q5. [Maths] Simplify: -5 - (-6)", ["-11", "1", "11", "-1"], "1", "-5 - (-6) = -5 + 6 = 1. Minus a minus becomes plus."),
    ("Q6. [Maths] A pair of packets of biscuits costs Sh. 1000. Find the cost of 7 similar packets of biscuits.", ["Sh. 3500", "Sh. 7000", "Sh. 500", "Sh. 3000"], "Sh. 3500", "1 pair = 2 packets = 1000, so 1 packet = 500. 7 x 500 = 3500."),
    ("Q7. [Maths] How far can a fox run into a circular forest?", ["All the way through", "Quarter way", "Halfway", "To the centre only"], "Halfway", "Trick! After halfway, the fox starts running OUT of the forest, not in."),
    ("Q8. [Science] How does a mosquito differ from a cockroach in terms of their lifecycle?", ["Both undergo complete metamorphosis", "Both undergo incomplete metamorphosis", "Mosquito undergoes incomplete metamorphosis, cockroach undergoes complete metamorphosis", "Mosquito undergoes complete metamorphosis, cockroach undergoes incomplete metamorphosis"], "Mosquito undergoes complete metamorphosis, cockroach undergoes incomplete metamorphosis", "Mosquito: egg - larva - pupa - adult (complete). Cockroach: egg - nymph - adult (incomplete, no pupa)."),
    ("Q9. [Science] Why does heat travel faster in a solid than in a gas?", ["Particles in a solid are closer together", "Particles in a gas are closer together", "Solids are hotter", "Gases have no particles"], "Particles in a solid are closer together", "Heat needs particles to pass it on. Solid particles are packed tight, so heat moves faster."),
    ("Q10. [RE] How does the school prayer assist a learner?", ["It makes the learner sleep", "It helps the learner start the day with discipline, respect and a calm mind", "It stops the learner from learning", "It makes the learner hungry"], "It helps the learner start the day with discipline, respect and a calm mind", "Prayer gives discipline, unity, respect for God, and settles the mind to learn."),
    ("Q11. [Maths] Simplify 2m - 8m + 13m", ["5m", "23m", "7m", "3m"], "7m", "2m - 8m = -6m, -6m + 13m = 7m."),
    ("Q12. [SST] Which country does Uganda border in the East?", ["Tanzania", "South Sudan", "DR Congo", "Kenya"], "Kenya", "Uganda borders Kenya in the East."),
    ("Q13. [Science] Why is heat unable to travel in a vacuum?", ["There are no particles to carry it", "Vacuum is too hot", "Vacuum is too cold", "Heat hates vacuum"], "There are no particles to carry it", "Heat by conduction and convection needs particles. In a vacuum there are no particles."),
    ("Q14. [Maths] Which of these is the net of a cylinder?", ["One circle and a triangle", "Two circles and a rectangle", "Three squares", "Two triangles and a rectangle"], "Two circles and a rectangle", "A cylinder net has 2 circles for top and bottom, and a rectangle for the curved side."),
    ("Q15. [SST] Name the major physical feature that is known for the formation of relief rainfall in Eastern Uganda.", ["Lake Victoria", "Mt. Rwenzori", "Mt. Elgon", "River Nile"], "Mt. Elgon", "Mt. Elgon in Eastern Uganda causes relief rainfall."),
    ("Q16. [English] Use the correct form: Sarah ........ meat to chicken. (Prefers, likes)", ["Likes", "Prefer", "Like", "Prefers"], "Prefers", "We say 'prefers ... to ...' when comparing two things. Sarah prefers meat to chicken."),
    ("Q17. [Maths] Molly is twice as old as Jolly. If the sum of their ages is 30, how old is Molly?", ["20 years", "10 years", "15 years", "30 years"], "20 years", "Jolly = 10, Molly = 2 x 10 = 20. 10 + 20 = 30."),
    ("Q18. [SST] What is a landlocked country?", ["A country with many lakes", "A country with no sea coast", "A country with a big airport", "A country near the sea"], "A country with no sea coast", "A landlocked country is surrounded by land and has no sea coast, e.g. Uganda."),
    ("Q19. [CRE] 'I AM WHO I AM.' To whom was the statement made?", ["Abraham", "Jacob", "Moses", "David"], "Moses", "God said 'I AM WHO I AM' to Moses at the burning bush."),
    ("Q20. [English] One of the following words means elephant in Kiswahili.", ["Tendo", "Rembo", "Pembo", "Tembo"], "Tembo", "Tembo means elephant in Kiswahili."),
]

if page == "Take Quiz":
    st.title("LearnEasy Quiz")
    st.write("Answer all questions, then click Submit.")
    name = st.text_input("Your Name")
    school = st.text_input("Your School")
    subject_choice = st.selectbox("Choose Subject to see its Learning Outcomes", list(learning_outcomes.keys()))
    st.subheader(f"Learning Outcomes: {subject_choice}")
    for outcome in learning_outcomes[subject_choice]:
        st.write(f"- {outcome}")
    answers = []
    for i, (q, options, correct, explain) in enumerate(questions):
        ans = st.radio(q, options, key=f"q{i}", index=None)
        answers.append(ans)
    if st.button("Submit Quiz - See My Results"):
        if not name or not school:
            st.warning("Please enter Your Name and Your School first.")
        elif st.session_state.submitted:
            st.info("You already submitted. Click Take Quiz Again below to start fresh.")
        else:
            score = 0
            for i in range(len(questions)):
                if answers[i] == questions[i][2]:
                    score = score + 1
            percentage = (score / len(questions)) * 100
            if percentage >= 80:
                grade = "Excellent"
            elif percentage >= 50:
                grade = "Good - Keep Practicing"
            else:
                grade = "Needs Practice"
            st.session_state.results.append({
                "Date & Time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "Name": name,
                "School": school,
                "Score": f"{score}/{len(questions)}",
                "Percentage": round(percentage),
                "Grade": grade,
            })
            save_results()
            st.session_state.submitted = True
            st.session_state.last_score = score
            st.session_state.last_percentage = round(percentage)
            st.session_state.last_grade = grade
            st.session_state.last_answers = list(answers)
            st.session_state.last_name = name
            st.rerun()
    if st.session_state.submitted:
        st.success(f"Well done {st.session_state.last_name}! You scored {st.session_state.last_score}/{len(questions)} = {st.session_state.last_percentage}% - {st.session_state.last_grade}")
        st.info("Your result has been SAVED. Your teacher can see it in Teacher Dashboard.")
        # Top 3 badge - simple and safe
        sorted_results = sorted(st.session_state.results, key=lambda x: int(x["Percentage"]), reverse=True)
        top3 = sorted_results[:3]
        my_pct = st.session_state.last_percentage
        rank = 0
        for idx in range(len(top3)):
            if int(top3[idx]["Percentage"]) == my_pct:
                rank = idx + 1
                break
        if rank == 1:
            st.balloons()
            st.success("🏆 🥇 GOLD - TOP 1! You are the Champion!")
        elif rank == 2:
            st.success("🏆 🥈 SILVER - TOP 2! Excellent work!")
        elif rank == 3:
            st.success("🏆 🥉 BRONZE - TOP 3! You made it!")
        st.subheader("See Your Answers + Explanations")
        saved = st.session_state.last_answers
        for i in range(len(questions)):
            q = questions[i]
            ans = saved[i] if i < len(saved) else ""
            st.write(f"Q{i+1}: {q}")
            st.write(f"Your answer: {ans}")
            elif page == "Teacher Dashboard":
    st.title("Teacher Dashboard")
    if "results" not in st.session_state:
        st.session_state.results = []
    if len(st.session_state.results) == 0:
        st.info("No results yet. Ask a student to take a quiz first, then come back here.")
    else:
        df = pd.DataFrame(st.session_state.results)
        st.write(f"Total attempts: {len(df)}")
        if "Percentage" in df.columns:
            st.write(f"Average score: {int(df['Percentage'].astype(int).mean())}%")
        st.subheader("All Results")
        st.dataframe(df)
        st.download_button("Download Results CSV", df.to_csv(index=False), "results.csv", "text/csv")
