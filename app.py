import streamlit as st
import pandas as pd
from spotify_scraper import generate_spotify_catalog # ייבוא הפונקציה מהמודול שלנו

st.set_page_config(layout="wide", page_title="Spotify Catalog Generator")

st.title("🎵 Spotify Catalog Generator")
st.markdown("Enter your Spotify API keys and a list of links (tracks, albums, or artists) to generate an Excel table with song details.")

# API Keys Input
st.sidebar.header("🔑 Spotify API Credentials")
client_id = st.sidebar.text_input("Spotify Client ID", type="password", help="Your Client ID from the Spotify Developer Dashboard")
client_secret = st.sidebar.text_input("Spotify Client Secret", type="password", help="Your Client Secret from the Spotify Developer Dashboard")

# Spotify Links Input
st.header("🔗 Enter Spotify Links")
spotify_urls_input = st.text_area("Paste Spotify links here (one link per line)", height=250, 
                                  placeholder="For example:\nhttps://open.spotify.com/track/your_track_id\nhttps://open.spotify.com/album/your_album_id\nhttps://open.spotify.com/artist/your_artist_id")

# Generate Button
if st.button("🚀 Generate Excel Table"):
    if not client_id or not client_secret:
        st.error("⚠️ Please enter both Spotify Client ID and Client Secret.")
    elif not spotify_urls_input:
        st.error("⚠️ Please enter at least one Spotify link.")
    else:
        urls_list = [url.strip() for url in spotify_urls_input.split('\n') if url.strip()]
        if not urls_list:
            st.error("⚠️ The list of links is empty or contains only whitespace. Please enter valid links.")
        else:
            st.info(f"Processing {len(urls_list)} links... This may take a few minutes, depending on the amount of data.")
            
            excel_data = None # Initialize excel_data
            with st.spinner('Processing data from Spotify... ⏳ Please wait.'):
                excel_data = generate_spotify_catalog(client_id, client_secret, urls_list)
            
            if excel_data:
                st.success("✅ Data processing complete!")
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_data, # Excel file data as bytes
                    file_name="spotify_catalog_generated.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_button"
                )
            else:
                st.error("❌ An error occurred during data processing. Please check the terminal console from which you ran the app for more details, or try again.")

st.sidebar.markdown("---")
st.sidebar.markdown("---")
st.sidebar.info("This application uses the Spotify API to collect data and potentially the Songlink/Odesli API (if integrated) to find additional links.")
st.sidebar.markdown("Developed by Sticky.")

# Instructions for running (will appear in the terminal):
# 1. Ensure the streamlit library is installed: pip install streamlit
# 2. Run the application: streamlit run app.py
