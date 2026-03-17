import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎵 מוריד שירים - גרסה עוקפת חסימות")

# שליפת העוגיות מה-Secrets של Streamlit
YT_COOKIES = st.secrets.get("youtube_cookies")

url = st.text_input("הכנס קישור:")
format_choice = st.radio("בחר פורמט:", ("MP3", "MP4"))

if st.button("הורד"):
    if url and YT_COOKIES:
        with st.spinner('מתחבר ליוטיוב...'):
            try:
                # יצירת קובץ זמני לעוגיות
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tfile:
                    tfile.write(YT_COOKIES)
                    cookie_path = tfile.name

                # הגדרות מתקדמות לעקיפת חסימות
                ydl_opts = {
                    'format': 'bestaudio/best' if format_choice == "MP3" else 'best',
                    'cookiefile': cookie_path,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'nocheckcertificate': True,
                    'quiet': True,
                    'no_warnings': True,
                    'outtmpl': 'downloaded_file.%(ext)s',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                with open(filename, "rb") as f:
                    st.download_button("לחץ להורדה סופית", f, file_name=filename)
                
                # ניקוי הקובץ הזמני
                os.unlink(cookie_path)
                
            except Exception as e:
                st.error(f"שגיאה: {e}")
    else:
        st.error("חסר קישור או שלא הוגדרו עוגיות ב-Secrets")
