import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="מוריד שירים", layout="centered")

st.title("🎵 מוריד שירים וסרטונים")
st.write("הכנס קישור, בחר פורמט והורד בקלות.")

# תיבת הזנת קישור
url = st.text_input("הכנס קישור (YouTube וכדומה):", placeholder="https://www.youtube.com/watch?v=...")

# בחירת פורמט
format_choice = st.radio("בחר פורמט הורדה:", ("MP3 (אודיו בלבד)", "MP4 (וידאו)"))

if st.button("הכן קובץ להורדה"):
    if url:
        with st.spinner('מעבד את הבקשה...'):
            try:
                # הגדרות עבור yt-dlp
                ydl_opts = {
                    'format': 'bestaudio/best' if "MP3" in format_choice else 'bestvideo+bestaudio/best',
                    'outtmpl': 'downloaded_file.%(ext)s',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                
                # כפתור הורדה בפועל למחשב המשתמש
                with open(filename, "rb") as file:
                    st.download_button(
                        label="לחץ כאן להורדת הקובץ",
                        data=file,
                        file_name=filename,
                        mime="audio/mpeg" if "MP3" in format_choice else "video/mp4"
                    )
                st.success("הקובץ מוכן!")
                
            except Exception as e:
                st.error(f"אירעה שגיאה: {e}")
    else:
        st.warning("נא להזין קישור תקין.")
