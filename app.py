import streamlit as st
from github import Github
from github import Auth
import time

st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")

st.title("🎵 Smart YouTube Downloader")

def get_github_client():
    if "GITHUB_TOKEN" not in st.secrets or "REPO_NAME" not in st.secrets:
        st.error("Missing Secrets!")
        return None, None
    auth = Auth.Token(st.secrets["GITHUB_TOKEN"])
    g = Github(auth=auth)
    return g, g.get_repo(st.secrets["REPO_NAME"])

def download_ui():
    g, repo = get_github_client()
    if not repo: return

    urls = st.text_area("הדבק קישורים (מופרדים בפסיקים או שורות חדשות):")
    format_type = st.radio("פורמט:", ["mp3", "mp4"], horizontal=True)

    if st.button("🚀 התחל הורדה"):
        if not urls:
            st.warning("נא להזין קישורים.")
            return

        clean_urls = ",".join([u.strip() for u in urls.replace("\n", ",").split(",") if u.strip()])
        
        try:
            workflow = repo.get_workflow("download.yml")
            
            # 1. הפעלת ה-Workflow
            with st.status("שולח בקשה ל-GitHub...", expanded=True) as status:
                workflow.create_dispatch(ref="main", inputs={"yt_urls": clean_urls, "format": format_type})
                status.write("⏳ ממתין שההרצה תתחיל (זה לוקח כמה שניות)...")
                
                # 2. זיהוי מספר הריצה (Run Number)
                # אנחנו מחפשים את הריצה הכי חדשה שנוצרה ב-30 שניות האחרונות
                run = None
                for _ in range(10): # מנסה למצוא את הריצה במשך 20 שניות
                    time.sleep(2)
                    runs = workflow.get_runs()
                    if runs.totalCount > 0:
                        latest_run = runs[0]
                        # אם הריצה במצב 'queued' או 'in_progress', זו הריצה שלנו
                        if latest_run.status in ["queued", "in_progress"]:
                            run = latest_run
                            break
                
                if not run:
                    status.update(label="❌ שגיאה: לא הצלחתי למצוא את הריצה ב-GitHub", state="error")
                    return

                run_number = run.run_number
                status.write(f"✅ זוהתה ריצה מספר: `{run_number}`")
                status.write("📥 מוריד ומעבד את הסרטונים (זה עשוי לקחת 1-3 דקות)...")

                # 3. מעקב אחרי סטטוס הריצה
                while run.status != "completed":
                    time.sleep(5)
                    run = repo.get_workflow_run(run.id) # רענון נתונים
                
                if run.conclusion == "success":
                    status.update(label="✅ ההורדה הושלמה!", state="complete")
                    
                    # 4. מציאת ה-Release והקובץ
                    tag = f"v{run_number}"
                    try:
                        # מחכה שניה שה-Release יתעדכן בשרתים של GitHub
                        time.sleep(2)
                        release = repo.get_release(tag)
                        assets = release.get_assets()
                        
                        if assets.totalCount > 0:
                            asset = assets[0] # לוקח את הקובץ הראשון (השיר או ה-ZIP)
                            download_url = asset.browser_download_url
                            
                            st.balloons()
                            st.success(f"הקובץ מוכן: **{asset.name}**")
                            
                            # כפתור הורדה ישירה
                            st.link_button(f"⬇️ הורד עכשיו: {asset.name}", download_url)
                            st.info("אם ההורדה לא מתחילה, לחץ קליק ימני ושמור בשם.")
                        else:
                            st.error("הריצה הצליחה אבל לא נמצא קובץ להורדה.")
                    except Exception:
                        st.error(f"לא הצלחתי למצוא את ה-Release עם התגית {tag}.")
                else:
                    status.update(label=f"❌ הריצה נכשלה (סטטוס: {run.conclusion})", state="error")

        except Exception as e:
            st.error(f"שגיאה כללית: {e}")

download_ui()
