import streamlit as st
from github import Github
import time
import requests

# הגדרות GitHub - מומלץ להשתמש ב-Secrets של Streamlit
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "Downloading-songs-from-YouTube-with-filtering" # שנה לשם המאגר שלך

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

st.title("🎵 Smart Downloader")

# קלט מהמשתמש
urls = st.text_input("הדבק קישורים (מופרדים בפסיקים):", placeholder="https://youtube.com/..., https://youtube.com/...")
format_choice = st.selectbox("בחר פורמט:", ["mp3", "mp4"])

if st.button("הורדה"):
    if not urls:
        st.error("אנא הכנס לפחות קישור אחד.")
    else:
        try:
            # 1. הפעלת ה-Workflow
            workflow = repo.get_workflow("download.yml") # וודא שזה שם הקובץ בגיטהאב
            workflow.create_dispatch(
                ref="main",
                inputs={
                    "yt_urls": urls,
                    "format": format_choice
                }
            )
            
            st.info("הבקשה נשלחה ל-GitHub Actions. ממתין ליצירת הקובץ...")
            
            # 2. זיהוי מספר הריצה (Run Number)
            # אנחנו מחכים רגע כדי שהריצה תתחיל להופיע ב-API
            time.sleep(5)
            runs = repo.get_workflow_runs()
            latest_run = runs[0]
            run_number = latest_run.run_number
            tag_name = f"v{run_number}"
            
            st.warning(f"מזהה ריצה: {run_number}. בודק אם ה-Release מוכן...")

            # 3. לולאת בדיקה ל-Release
            max_retries = 30  # כ-5 דקות המתנה מקסימום
            found = False
            
            status_placeholder = st.empty()
            
            for i in range(max_retries):
                try:
                    release = repo.get_release(tag_name)
                    assets = release.get_assets()
                    if assets.totalCount > 0:
                        download_url = assets[0].browser_download_url
                        st.success("✅ הקובץ מוכן!")
                        st.balloons()
                        st.markdown(f"### [לחץ כאן להורדה ישירה]({download_url})")
                        found = True
                        break
                except:
                    status_placeholder.text(f"מעבד... ({i+1}/{max_retries})")
                
                time.sleep(10) # בדיקה כל 10 שניות
            
            if not found:
                st.error("התהליך לוקח יותר מדי זמן או שנכשל ב-GitHub. בדוק את דף ה-Actions.")
                
        except Exception as e:
            st.error(f"שגיאה באדום: {str(e)}")
