import streamlit as st
import gspread
import pandas as pd
import io
from google.oauth2.service_account import Credentials

SHEET_ID = "1G2PdfSMPXXlZCnumPYpAPkyIU84JrJ9wq97SHI0FoFg"

def get_creds():
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
    else:
        creds_dict = dict(st.secrets)
    # --- FIX BROKEN PRIVATE KEY ---
    pk = creds_dict["private_key"]
    pk = pk.replace("\\n", "\n").replace("\r", "")
    body = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").replace("\n", "").replace(" ", "")
    body = "".join([c for c in body if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="])
    body += "=" * (-len(body) % 4)
    body = "\n".join([body[i:i+64] for i in range(0, len(body), 64)])
    creds_dict["private_key"] = "-----BEGIN PRIVATE KEY-----\n" + body + "\n-----END PRIVATE KEY-----\n"
    return Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])

def get_worksheet():
    client = gspread.authorize(get_creds())
    return client.open("learneasy-scores2").sheet1

def save_to_sheet(name, school, score, percentage, grade):
    try:
        ws = get_worksheet()
        ws.append_row([name, school, score, percentage, grade])
        return True
    except Exception as e:
        st.error(f"Could not save: {e}")
        return False

# --- MENU ---
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to:", ["Take Quiz", "Teacher Dashboard"])

# ================= TAKE QUIZ =================
if page == "Take Quiz":
    st.title("LearnEasy Quiz")
    st.write("Welcome! Answer all questions.")

    name = st.text_input("Your Name")
    school = st.text_input("Your School")
learning_outcomes = {
    # --- MATHS - 12 Topics ---
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

    # --- SCIENCE ---
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

    # --- ENGLISH ---
    "P5-E-T1-01 Vehicle Repair": ["Use vocabulary - engine, tyre, steering, windscreen, seat belt","Construct sentences about vehicle parts","Read passage and answer questions"],
    "P5-E-T1-02 Print Media": ["Use vocabulary - advertisement, reporter, article, column","Read advertisement","Write advertisement"],
    "P5-E-T1-03 Travelling": ["Use vocabulary - journey, fare, ticket, luggage","Use Past Simple and Past Continuous","Write guided composition on a journey"],
    "P5-E-T2-04 Letter Writing": ["Write friendly and formal letters","Use correct format - address, date, salutation, body, closing","Use Future Simple Tense"],
    "P5-E-T2-05 Communication": ["Use vocabulary - post office, telephone, internet, email","Write dialogue","Use structures for asking and giving information"],
    "P5-E-T3-06 Culture": ["Use vocabulary - nationality, language","Talk about nationalities - Ugandan, Kenyan, Tanzanian","Read text on culture"],
    "P5-E-T3-07 Peace & Security": ["Use vocabulary - peace, security, soldier, police","Construct sentences","Read passage on peace"],
    "P5-E-T3-08 Services - Banks": ["Use vocabulary - bank, account, deposit, withdraw","Fill bank forms","Write sentences on banking"],
    "P5-E-ALL-09 Grammar & Punctuation": ["Use capital letters, full stop, question mark, apostrophe","Identify nouns, pronouns, verbs, adjectives, adverbs, prepositions, conjunctions","Use tenses correctly","Use synonyms and antonyms"],

    # --- SST ---
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

    # --- RELIGIOUS EDUCATION ---
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

    # --- KISWAHILI ---
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
    ("Q1. [Maths] What is the place value of 5 in 5,432?", ["5000", "500", "50", "5"], "5000", "5 is in the thousands place. 5 thousands = 5000. The digits are: 5 thousands, 4 hundreds, 3 tens, 2 ones."),
    ("Q2. [Maths] What is 1/2 + 1/4?", ["3/4", "2/6", "1/4", "2/4"], "3/4", "Change to same denominator: 1/2 = 2/4. Then 2/4 + 1/4 = 3/4."),
    ("Q3. [English] Choose the correct sentence.", ["She goes to school every day.", "She go to school every day.", "she goes to school every day", "She goes to school every day"], "She goes to school every day.", "The correct sentence starts with a capital letter, ends with a full stop, and the verb agrees with the subject. 'She goes' is correct, not 'She go'."),
    ("Q4. [Science] Which gas do plants use to make food?", ["Carbon dioxide", "Oxygen", "Nitrogen", "Hydrogen"], "Carbon dioxide", "Plants use carbon dioxide from the air + water + sunlight to make food in photosynthesis. They give out oxygen."),
    ("Q5. [Maths] What is 12 x 8?", ["96", "86", "108", "84"], "96", "12 x 8 = 96. Think: 10 x 8 = 80, 2 x 8 = 16, 80 + 16 = 96."),
    ("Q6. [SST] What is the capital city of Uganda?", ["Kampala", "Entebbe", "Jinja", "Mbarara"], "Kampala", "Kampala is the capital city of Uganda. It is where the government and Parliament sit. Entebbe has the airport, Jinja is the source of the Nile."),
    ("Q7. [English] What is the opposite of 'happy'?", ["Sad", "Glad", "Joyful", "Cheerful"], "Sad", "The opposite of happy is sad. Glad, joyful and cheerful all mean almost the same as happy."),
    ("Q8. [Science] Which animal is a mammal?", ["Cow", "Chicken", "Fish", "Frog"], "Cow", "A mammal gives birth to live young, breastfeeds its babies with milk, has hair/fur, and breathes with lungs. Birds, fish, frogs and insects are not mammals."),
    ("Q9. [Maths] What is 100 - 37?", ["63", "67", "73", "37"], "63", "100 - 37 = 63. Subtract 30 to get 70, then subtract 7 more to get 63."),
    ("Q10. [English] Fill in: ___ apple is red.", ["An", "The", "A", "Some"], "The", "We use 'The' because we are talking about a specific apple that we both know. 'An' is for any one apple, not a specific one."),
    ("Q11. [Maths] Simplify 2m - 8m + 13m", ["7m", "23m", "3m", "19m"], "7m", "2m - 8m = -6m. Then -6m + 13m = 7m. We add and subtract like terms."),
    ("Q12. [SST] Which country does Uganda border in the East?", ["DR Congo", "Kenya", "Tanzania", "South Sudan"], "Kenya", "Kenya is to the east of Uganda where the sun rises. DR Congo is to the west where the sun sets."),
    ("Q13. [Science] Why is heat unable to travel in a vacuum?", ["There are no particles to carry it", "Vacuum is too cold", "Heat needs light", "Vacuum blocks heat"], "There are no particles to carry it", "Heat by conduction and convection needs particles to pass it along. A vacuum has no particles, so heat cannot travel that way."),
    ("Q14. [Maths] Which of these is the net of a cylinder?", ["2 circles and a rectangle", "1 circle and a triangle", "3 squares", "2 triangles and a rectangle"], "2 circles and a rectangle", "A cylinder has 2 circular ends (top and bottom) and 1 curved side that opens into a rectangle."),
    ("Q15. [SST] Name the major physical feature that is known for the formation of relief rainfall in Eastern Uganda.", ["Mt Elgon", "Mt Rwenzori", "Lake Victoria", "Mt Mufumbiro"], "Mt Elgon", "Mt Elgon in Eastern Uganda forces moist air to rise, cool and form relief rainfall on its slopes."),
    ("Q16. [English] Sarah ........ meat to chicken. (Prefers, likes)", ["Prefers", "Likes", "Prefer", "Like"], "Prefers", "We use 'Prefers' because Sarah likes meat MORE than chicken. 'Prefers... to...' shows a choice between two things. Sarah is one person, so we add 's' - She prefers."),
    ("Q17. [Maths] Molly is twice as old as Jolly. If the sum of their ages is 30, how old is Molly?", ["20", "10", "15", "30"], "20", "Let Jolly = 1 part, Molly = 2 parts. Total = 3 parts = 30. 1 part = 30 / 3 = 10. So Molly = 2 x 10 = 20 years."),
    ("Q18. [SST] What is a landlocked country?", ["A country with no sea coast", "A country with many lakes", "A country with a big sea port", "A country surrounded by water"], "A country with no sea coast", "A landlocked country has no coastline on the sea or ocean. It is surrounded by other countries on all sides. Uganda is landlocked."),
    ("Q19. [CRE] 'I AM WHO I AM.' To whom was the statement made?", ["Moses", "Abraham", "Jacob", "Aaron"], "Moses", "God said 'I AM WHO I AM' to Moses at the burning bush in Exodus 3, when Moses asked for God's name before going to Pharaoh in Egypt."),
    ("Q20. [English] One of the following words means elephant in Kiswahili.", ["Tembo", "Simba", "Nyani", "Paka"], "Tembo", "In Kiswahili, elephant = Tembo. Simba = lion, Nyani = monkey, Paka = cat."),
]
    if st.button("🔄 New Pupil - Start Fresh Quiz"): [st.session_state.pop(k) for k in list(st.session_state.keys()) if k.startswith("q")]; st.rerun()
    answers = []
    for i, t in enumerate(questions):
        q, options, correct, exp = (t + ("",) * 4)[:4]
        ans = st.radio(f"{q}", options, key=f"q{i}", index=None)
        answers.append(ans)

    if st.button("Submit Quiz - See My Results"):
        if not name or not school:
            st.warning("Please enter your Name and School first.")
        else:
            score = sum(1 for (q, opts, corr, exp), ans in zip(questions, answers) if ans == corr)
            percentage = (score / len(questions)) * 100
            if percentage >= 90:
                grade, comment = "D1", "Excellent! Keep it up!"
            elif percentage >= 75:
                grade, comment = "D2", "Very good!"
            elif percentage >= 60:
                grade, comment = "C3", "Good, keep working!"
            elif percentage >= 50:
                grade, comment = "C4", "Fair, you can improve!"
            else:
                grade, comment = "F9", "Don't give up, try again!"

            st.success(f"🎉 Well done, {name}!")
            st.write(f"Score: {score} out of {len(questions)}")
            st.write(f"Percentage: {percentage:.0f}%")
            st.write(f"Grade: {grade}")
            st.write(f"Comment: {comment}")
            st.subheader("Review - See correct answers and explanations")
            for i, t in enumerate(questions):
                q, options, correct, exp = (t + ("",) * 4)[:4]
                ans = answers[i]
                if ans == correct:
                    st.success(f"Q{i+1}: {q} - Correct!")
                else:
                   st.error(f"Q{i+1}: {q} - Wrong. Your answer: {ans}. Correct answer: {correct}")
                if exp:
                    st.info(f"Explanation: {exp}")

            if save_to_sheet(name, school, score, percentage, grade):
                st.info("✅ Your result has been saved!")

# ================= TEACHER DASHBOARD =================
if page == "Teacher Dashboard":
    st.title("📊 Teacher Dashboard - LearnEasy")
    password = st.text_input("Enter Teacher Password", type="password")
    if password == "teacher123":
        st.success("Welcome Teacher!")
        try:
                ws = get_worksheet()
                data = ws.get_all_records()
                df = pd.DataFrame(data)
                df.columns = [str(c).strip().capitalize() for c in df.columns]
                df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
                df["Percentage"] = pd.to_numeric(df["Percentage"].astype(str).str.replace("%", "").str.strip(), errors="coerce")
                if len(df) == 0:
                    st.info("No results yet.")
                else:
                    col1, col2 = st.columns(2)
                    col1.metric("Total Learners", len(df))
                    col2.metric("Average Score", f"{df['Percentage'].mean():.1f}%")
                    top3 = df.sort_values(by="Percentage", ascending=False).head(3)
                    st.subheader("🏆 Top 3 Performers")
                    medals = ["🥇", "🥈", "🥉"]
                    for i, (idx, row) in enumerate(top3.iterrows()): st.success(f"{medals[i]} {row['Name']} - Score: {row['Score']} ({row['Percentage']}%)")
                    st.balloons()
                    st.write("Search by name:")
                    search = st.text_input("Type name...")
                    if search:
                        df = df[df['Name'].astype(str).str.contains(search, case=False)]
                    st.dataframe(df)
                    st.download_button("📥 Download Results", df.to_csv(index=False).encode("utf-8"), "results.csv", "text/csv")
        except Exception as e:
                st.error(f"Could not load results: {e}")        
    elif password != "":
                st.error("Wrong password")
