import streamlit as st
import yt_dlp
import os
import tempfile

# הגדרות עמוד בסיסיות
st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("🎵 מוריד שירים וסרטונים")

# שליפת העוגיות מה-Secrets של Streamlit
# וודא שהגדרת ב-Secrets משתנה בשם youtube_cookies
YT_COOKIES = st.secrets.get("youtube_cookies")

url = st.text_input("הכנס קישור מיוטיוב:", placeholder="https://www.youtube.com/watch?v=...")
format_choice = st.radio("בחר פורמט הורדה:", ("MP3 (שמע)", "MP4 (וידאו)"))

if st.button("הכן קובץ להורדה"):
    if not url:
        st.error("נא להזין קישור.")
    elif not YT_COOKIES:
        st.error("שגיאה: לא נמצאו עוגיות במערכת. נא להגדיר אותן ב-Secrets.")
    else:
        with st.spinner('מעבד את הבקשה (זה עשוי לקחת רגע)...'):
            try:
                # יצירת קובץ זמני עבור העוגיות כדי ש-yt-dlp יוכל לקרוא אותן
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tfile:
                    tfile.write(YT_COOKIES)
                    cookie_path = tfile.name

                # הגדרות אופטימליות לעקיפת חסימות בשרתים ציבוריים
                ydl_opts = {
                    # שימוש ב-'best' עוזר להימנע משגיאות פורמט כשאין JS runtime
                    'format': 'bestaudio/best' if "MP3" in format_choice else 'best',
                    'cookiefile': cookie_path,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'nocheckcertificate': True,
                    'quiet': True,
                    'outtmpl': 'downloaded_file.%(ext)s',
                }

                # ביצוע ההורדה לשרת הזמני
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    # אם בחרנו MP3, yt-dlp לפעמים מוריד כ-m4a/webm, נעדכן את השם להורדה
                    final_filename = filename
                
                # יצירת כפתור הורדה למחשב המשתמש
                with open(final_filename, "rb") as file:
                    st.download_button(
                        label="⬇️ לחץ כאן להורדת הקובץ למחשב",
                        data=file,
                        file_name=final_filename,
                        mime="audio/mpeg" if "MP3" in format_choice else "video/mp4"
                    )
                
                st.success("הקובץ מוכן בהצלחה!")
                
                # ניקוי קבצים זמניים
                if os.path.exists(cookie_path):
                    os.unlink(cookie_path)
                
            except Exception as e:
                st.error(f"אירעה שגיאה בתהליך: {e}")
