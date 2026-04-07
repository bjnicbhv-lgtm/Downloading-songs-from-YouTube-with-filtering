import streamlit as st
from github import Github
from github import Auth
import time

# הגדרות דף
st.set_page_config(page_title="YouTube Downloader", page_icon="🎵", layout="centered")

st.title("🎵 Smart YouTube Downloader")
st.write("הורד שירים ישירות ל-GitHub וקבל קישור להורדה")

def get_github_client():
    if "GITHUB_TOKEN" not in st.secrets or "REPO_NAME" not in st.secrets:
        st.error("שגיאה: חסרים Secrets (GITHUB_TOKEN / REPO_NAME)")
        return None, None
    auth = Auth.Token(st.secrets["GITHUB_TOKEN"])
    g = Github(auth=auth)
    try:
        repo = g.get_repo(st.secrets["REPO_NAME"])
        return g, repo
    except Exception as e:
        st.error(f"לא הצלחתי להתחבר למאגר: {e}")
        return None, None

def run_downloader():
    g, repo = get_github_client()
    if not repo:
        return

    # ממשק קלט
    urls = st.text_area("הדבק קישורים מיוטיוב (מופרדים בפסיקים או שורות חדשות):", height=150)
    format_type = st.radio("בחר פורמט:", ["mp3", "mp4"], horizontal=True)

    if st.button("🚀 התחל הורדה", use_container_width=True):
        if not urls:
            st.warning("בבקשה הזן לפחות קישור אחד.")
            return

        # ניקוי הקישורים
        cleaned_urls = ",".join([u.strip() for u in urls.replace("\n", ",").split(",") if u.strip()])
        
        try:
            workflow = repo.get_workflow("download.yml")
            
            with st.status("מתחיל תהליך...", expanded=True) as status:
                # הפעלת ה-Workflow
                status.write("📡 שולח פקודה ל-GitHub Actions...")
                workflow.create_dispatch(ref="main", inputs={"yt_urls": cleaned_urls, "format": format_type})
                
                # חיפוש הריצה שהתחילה
                run = None
                for _ in range(15):  # ניסיונות למצוא את הריצה (30 שניות)
                    time.sleep(2)
                    runs = workflow.get_runs()
                    if runs.totalCount > 0:
                        latest_run = runs[0]
                        if latest_run.status in ["queued", "in_progress"]:
                            run = latest_run
                            break
                
                if not run:
                    status.update(label="❌ שגיאה: GitHub לא התחיל את הריצה בזמן.", state="error")
                    return

                run_number = run.run_number
                status.write(f"✅ הריצה החלה! (מספר ריצה: `{run_number}`)")
                status.write("⏳ מוריד ומעבד את הקבצים... זה לוקח כדקה או שתיים.")

                # המתנה לסיום
                while run.status != "completed":
                    time.sleep(5)
                    run = repo.get_workflow_run(run.id)
                
                if run.conclusion == "success":
                    status.update(label="✅ התהליך הסתיים בהצלחה!", state="complete")
                    
                    # קבלת ה-Release והקובץ
                    time.sleep(3) # זמן קצר לעדכון ה-API
                    release = repo.get_release(f"v{run_number}")
                    assets = release.get_assets()
                    
                    if assets.totalCount > 0:
                        asset = assets[0]
                        st.balloons()
                        st.success(f"הקובץ מוכן: **{asset.name}**")
                        st.link_button(f"⬇️ הורד עכשיו: {asset.name}", asset.browser_download_url)
                    else:
                        st.error("הריצה הצליחה אך לא נמצא קובץ ב-Release.")
                else:
                    status.update(label=f"❌ הריצה נכשלה (סטטוס: {run.conclusion})", state="error")

        except Exception as e:
            st.error(f"שגיאה בתקשורת עם GitHub: {e}")

run_downloader()

# הצגת היסטוריית הורדות בציד (Sidebar)
with st.sidebar:
    st.title("הגדרות")
    if "REPO_NAME" in st.secrets:
        st.write(f"Repository: `{st.secrets['REPO_NAME']}`")
    st.info("הקבצים נשמרים ב-Releases של המאגר שלך ב-GitHub.")
