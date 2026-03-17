import streamlit as st
import requests
import time

st.set_page_config(page_title="YouTube to PC", page_icon="🎵")
st.title("🎵 הורדה חכמה ומסונכרנת")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
GITHUB_USER = st.secrets.get("GITHUB_USER")
REPO_NAME = st.secrets.get("REPO_NAME")

url = st.text_input("הדבק קישור מיוטיוב:")
format_choice = st.selectbox("בחר פורמט:", ["mp3", "mp4"])

if st.button("הפעל הורדה"):
    if url and GITHUB_TOKEN:
        with st.spinner('יוצר קשר עם שרת ההורדות...'):
            # 1. הפעלת ה-Workflow
            api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/actions/workflows/download.yml/dispatches"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"ref": "main", "inputs": {"yt_urls": url, "format": format_choice}}
            
            response = requests.post(api_url, headers=headers, json=data)
            
            if response.status_code == 204:
                st.success("✅ הפקודה התקבלה! השרת מתחיל לעבוד על השיר שלך.")
                
                # 2. שלב ההמתנה החכם
                placeholder = st.empty()
                status_text = st.empty()
                
                # נחכה קצת שהריצה תופיע במערכת
                time.sleep(5) 
                
                # נמצא את ה-ID של הריצה האחרונה שהתחילה עכשיו
                runs_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/actions/runs?per_page=1"
                run_data = requests.get(runs_url, headers=headers).json()
                current_run_id = run_data['workflow_runs'][0]['id']
                run_number = run_data['workflow_runs'][0]['run_number']
                
                start_time = time.time()
                while True:
                    # בדיקת מצב הריצה הספציפית
                    check_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/actions/runs/{current_run_id}"
                    status_res = requests.get(check_url, headers=headers).json()
                    status = status_res.get("status")
                    conclusion = status_res.get("conclusion")
                    
                    elapsed = int(time.time() - start_time)
                    status_text.text(f"מצב עבודה: {status}... ({elapsed} שניות)")
                    
                    if status == "completed":
                        if conclusion == "success":
                            # רק כשהריצה הספציפית הצליחה, נחפש את ה-Release שלה
                            rel_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/releases/tags/run-{run_number}"
                            rel_res = requests.get(rel_url, headers=headers)
                            
                            if rel_res.status_code == 200:
                                assets = rel_res.json().get("assets", [])
                                if assets:
                                    download_url = assets[0]["browser_download_url"]
                                    status_text.empty()
                                    st.balloons()
                                    st.markdown(f"### 🎉 השיר החדש מוכן!")
                                    st.link_button("⬇️ הורד את השיר האחרון עכשיו", download_url)
                                    break
                        else:
                            st.error("השרת נתקל בבעיה בהורדת השיר הספציפי הזה.")
                            break
                    
                    if elapsed > 300: # הגבלת המתנה ל-5 דקות
                        st.warning("ההורדה לוקחת יותר מדי זמן. בדוק ידנית בגיטהאב.")
                        break
                        
                    time.sleep(10) # בדיקה כל 10 שניות
            else:
                st.error(f"שגיאה: {response.status_code}")
