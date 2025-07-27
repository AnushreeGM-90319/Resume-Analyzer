import streamlit as st
import pandas as pd
import time, datetime, random
from pyresparser import ResumeParser
import pymysql
import spacy
from streamlit_tags import st_tags
import config
from utils import get_table_download_link, pdf_reader, show_pdf
from courses_data import job_titles_courses, resume_videos, interview_videos
import streamlit as st
import base64
import io

nlp = spacy.load("en_core_web_sm")

def fetch_yt_video(link):
    import pafy
    video = pafy.new(link)
    return video.title


def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for i, (c_name, c_link) in enumerate(course_list[:no_of_reco]):
        st.markdown(f"({i+1}) [{c_name}]({c_link})")
        rec_course.append(c_name)
    return rec_course


connection = pymysql.connect(host='localhost', user='root', password='', db='resume_analyzer')
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills,
                courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (
    name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


st.set_page_config(
    page_title="SmartHire | Find your dream candidate",
    page_icon='./Logo/s6951lA.png',
)


def run():
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    st.markdown("""
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
        integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    """, unsafe_allow_html=True)

    st.markdown("""
        <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #FFFFFF; height: 100px">
        <a class="navbar-brand" href="https://youtube.com/dataprofessor" target="_blank">Data Professor</a>

        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
            <li class="nav-item active">
                        <a href="#" className="flex items-center mr-4 ">
                <img src="https://i.imgur.com/1K24qVG.png" height=50px className="" alt="Flowbite Logo" />
            </a>
            </li>
            <li class="nav-item active">
                <a class="nav-link mt-1  px-0 text-dark" href="#">Home <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item active">
                <a class="nav-link mt-1 text-dark" href="#">Jobs <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item active">
                <a class="nav-link mt-1 text-dark" href="#">Employers <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item active">
                <a class="nav-link mt-1 px-1 text-dark" href="#">Blog <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item active">
                <a class="nav-link mt-1 px-1 text-dark" href="#">About <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item active">
                <a class="nav-link mt-1 px-1 text-dark" href="#">Candidates<span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item active">
                <a class="nav-link mt-1 px-1 text-dark" href="https://smarthire-2-8bbc57.ingress-erytho.ewp.live/user-dashboard">Continue to dashboard<span class="sr-only">(current)</span></a>
            </li>
            </li>
            </ul>
        </div>
        </nav>
        """, unsafe_allow_html=True)

    st.title("Smart Resume Analyser")
    choice = 'Normal User'

    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)

    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(25) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills VARCHAR(300) NOT NULL,
                     Recommended_skills VARCHAR(300) NOT NULL,
                     Recommended_courses VARCHAR(600) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])

        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                 # Use a more robust method to read the file content
                file_content = pdf_file.read()
                f.write(file_content)
            st.markdown(show_pdf(save_image_path), unsafe_allow_html=True)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_image_path)
                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown(
                        '''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                        unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                        unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                        unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')

                all_skills = [skill.lower() for skill in resume_data['skills']]
                
                job_titles = []
                for title, courses in job_titles_courses.items():
                     if any(keyword.lower() in all_skills for course in courses for keyword in [skill for sublist in [item[0].lower().split(' ') for item in courses] for skill in sublist ]):
                         job_titles.append(title)

                if not job_titles:
                    st.error("** No Matching job title found please try again with valid resume **")

                else:
                   
                    best_job_title = job_titles[0]
                    st.success(
                        f"**Based on your skills, the best matching job title is: {best_job_title}**")

                    user_pref = st.text_input(
                        "If you have a different preference for a job title, enter it here (otherwise, press Enter):",
                        value=best_job_title)

                    recommended_skills = []
                    rec_course = []

                    # Updated logic to check if any key contains user input
                    selected_courses = None
                    for key, courses in job_titles_courses.items():
                        if user_pref.lower() in key.lower():
                           selected_courses = courses
                           break
                    

                    if selected_courses:
                        # Flatten the list of courses and extract skills
                        recommended_skills = list(set([skill for sublist in [item[0].lower().split(' ') for item in selected_courses] for skill in sublist ]))
                        
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown(
                           '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                           unsafe_allow_html=True)
                        # Recommend courses
                        rec_course = course_recommender(selected_courses)

                    else:
                        st.warning("Please select a valid job title from the specified categories.")

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html=True)

                if 'Declaration' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration✍/h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                        unsafe_allow_html=True)

                if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 37
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Writing Score: ' + str(score) + '**')
                st.warning("** Note: This score is calculated based on the content that you have added in your Resume. **")

                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                # res_vid_title = fetch_yt_video(resume_vid)
                res_vid_title = "Resume Tips For Freshers | How To Write A Resume"
                st.subheader("✅ **" + res_vid_title + "**")
                # print(resume_vid,"kkkkk")
                resume_vid = "https://www.youtube.com/watch?v=HQqqQx5BCFY"
                st.video(resume_vid)

                # Interview Preparation Video
                st.header("**Bonus Video for Interview👨‍💼 Tips💡**")
                # interview_vid = random.choice(interview_videos)
                # int_vid_title = fetch_yt_video(interview_vid)
                int_vid_title = "Modern Hire interview questions - and how to answer them!"
                st.subheader("✅ **" + int_vid_title + "**")
                interview_vid = "https://www.youtube.com/watch?v=XCjosBT3Gy8"
                st.video(interview_vid)

                connection.commit()

            else:
                st.error('Something went wrong..')
    else:
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'machine_learning_hub' and ad_password == 'mlhub123':
                st.success("Welcome Kushal")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills',
                                                 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'),
                            unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels,
                             title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(df, values=values, names=labels,
                             title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)


            else:
                st.error("Wrong ID & Password Provided")


run()