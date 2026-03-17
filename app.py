import streamlit as st
import yt_dlp
import os
import tempfile

# הגדרות עמוד
st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("🎵 מוריד שירים וסרטונים - גרסה יציבה")

# שליפת עוגיות מה-Secrets
YT_COOKIES = st.secrets.get("youtube_cookies")

url = st.text_input("הכנס קישור מיוטיוב:", placeholder="https://www.youtube.com/watch?v=...")
format_choice = st.radio("בחר פורמט הורדה:", ("MP3 (שמע)", "MP4 (וידאו)"))

if st.button("הכן קובץ להורדה"):
    if not url:
        st.error("נא להזין קישור.")
    elif not YT_COOKIES:
        st.error("שגיאה: לא נמצאו עוגיות ב-Secrets. יש לעדכן אותן כדי למנוע חסימה.")
    else:
        with st.spinner('מתחבר ליוטיוב ומכין את הקובץ...'):
            try:
                # יצירת קובץ עוגיות זמני
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tfile:
                    tfile.write(YT_COOKIES)
                    cookie_path = tfile.name

                # הגדרות למניעת שגיאות Signature ו-403
                ydl_opts = {
                    # שימוש ב-best הוא הקריטי ביותר כשאין JS runtime בשרת
                    'format': 'bestaudio/best' if "MP3" in format_choice else 'best',
                    'cookiefile': cookie_path,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'nocheckcertificate': True,
                    'quiet': True,
                    'outtmpl': 'downloaded_file.%(ext)s',
                    # הגדרה לעקיפת מגבלות הנגן שמופיעות בלוגים
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                
                # כפתור הורדה למשתמש
                with open(filename, "rb") as file:
                    st.download_button(
                        label="⬇️ לחץ כאן להורדת הקובץ",
                        data=file,
                        file_name=filename,
                        mime="audio/mpeg" if "MP3" in format_choice else "video/mp4"
                    )
                
                st.success("הקובץ מוכן!")
                
                # ניקוי קבצים זמניים
                if os.path.exists(cookie_path):
                    os.unlink(cookie_path)
                
            except Exception as e:
                st.error(f"אירעה שגיאה: {e}")
                st.info("טיפ: אם השגיאה נמשכת, וודא שהעוגיות ב-Secrets מעודכנות ושהן בפורמט Netscape.")
