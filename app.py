import streamlit as st
from github import Github
from github import Auth

# הגדרות דף
st.set_page_config(page_title="YouTube Downloader", page_icon="📥", layout="centered")

st.title("🎵 YouTube Downloader (via GitHub Actions)")

def run_github_action(urls, format_type):
    try:
        # בדיקת Secrets
        if "GITHUB_TOKEN" not in st.secrets or "REPO_NAME" not in st.secrets:
            st.error("שגיאה: הגדרות ה-Secrets (TOKEN/REPO_NAME) חסרות ב-Streamlit.")
            return

        # התחברות ל-GitHub
        auth = Auth.Token(st.secrets["GITHUB_TOKEN"])
        g = Github(auth=auth)
        repo = g.get_repo(st.secrets["REPO_NAME"])

        # קריאה לקובץ ה-Workflow הספציפי שלך
        workflow = repo.get_workflow("download.yml")
        
        # הפעלת ה-Workflow עם הקלטים
        workflow.create_dispatch(
            ref="main",  # וודא שה-Branch הראשי שלך אכן נקרא main
            inputs={
                "yt_urls": urls,
                "format": format_type
            }
        )
        return True
    except Exception as e:
        st.error(f"אירעה שגיאה: {e}")
        return False

# ממשק משתמש
st.subheader("הכנס קישורים להורדה")
urls_input = st.text_area("הדבק קישורים מיוטיוב (מופרדים בפסיקים או שורות חדשות):", height=150)
format_choice = st.selectbox("בחר פורמט:", ["mp3", "mp4"])

if st.button("🚀 התחל הורדה"):
    if not urls_input:
        st.warning("נא להזין קישורים.")
    else:
        # ניקוי הקישורים והפיכתם למחרוזת אחת מופרדת בפסיקים
        cleaned_urls = ",".join([u.strip() for u in urls_input.replace("\n", ",").split(",") if u.strip()])
        
        with st.spinner("שולח בקשה ל-GitHub..."):
            success = run_github_action(cleaned_urls, format_choice)
            
            if success:
                st.balloons()
                st.success("✅ הפעולה נשלחה בהצלחה!")
                st.info("ההורדה מתבצעת כעת בשרתי GitHub. התהליך לוקח 1-3 דקות.")
                
                # קישור מהיר לדף ה-Releases שבו יופיע הקובץ
                repo_url = st.secrets["REPO_NAME"]
                st.markdown(f"### [🔗 לחץ כאן למעבר להורדת הקבצים](https://github.com/{repo_url}/releases)")
                st.write("הקובץ החדש יופיע בראש הרשימה ברגע שהתהליך יסתיים.")

# הצגת סטטוס חיבור בסיסי ב-Sidebar
with st.sidebar:
    st.write("---")
    if "REPO_NAME" in st.secrets:
        st.write(f"Connected to: `{st.secrets['REPO_NAME']}`")
        st.write(f"Workflow file: `download.yml`")
