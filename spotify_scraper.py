import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re
import time
from io import BytesIO # Required to handle Excel file in memory

# הערה: קונפיגורציית SPOTIPY_CLIENT_ID ו-SPOTIPY_CLIENT_SECRET תועבר כפרמטרים לפונקציה הראשית.
# הגדרת OUTPUT_FILE כאן היא רק למקרה שנרצה להריץ את הסקריפט ישירות (לא מומלץ כשיש אפליקציית Streamlit).
# OUTPUT_FILE = 'spotify_catalog.xlsx' 
# --------------------

# רשימת קישורי Spotify לעיבוד.
# המשתמש צריך לערוך רשימה זו ולהוסיף את קישורי השירים, האלבומים והאמנים הרצויים.
# לדוגמה:
# song_and_album_urls = [
#     "https://open.spotify.com/track/your_track_id_here",
#     "https://open.spotify.com/album/your_album_id_here",
#     "https://open.spotify.com/artist/your_artist_id_here",
# ]
song_and_album_urls = [
    # סינגלים
    "https://open.spotify.com/track/4EhADWdV6hJgsuLR8yu3e2?si=7a54365467894d88",
    "https://open.spotify.com/track/0kbBhomoyHwQPqeJd8iRCu?si=bd9016ee115e414a",
    "https://open.spotify.com/track/4W8YBNdMGAieA2E3E09B2Z?si=0af43f48ad8c4659",
    "https://open.spotify.com/track/5chDfxxzSyVBcItEhltwek?si=b7586007a8ab4b3a",
    "https://open.spotify.com/track/5oo7aB8JLbPcE7rzNXCZ5d?si=884050b698684184",
    "https://open.spotify.com/track/1vfEWrLsBqwhuJ73bLaYpx?si=94debbbab6dc4afc",
    "https://open.spotify.com/track/3vz36eCnAxDtR7sslvLBhr?si=fa94f169eaf24dc7",
    # אלבומים
    "https://open.spotify.com/album/4N4yHAXd3i4QL6ojBckdbo?si=TN_jiavRSW2bwa48aX6g8g",
    "https://open.spotify.com/album/1YFdhcXAegRmPSFwPTjO9N?si=zlNCUYSHRLOjIO2kDhAYhQ",
    "https://open.spotify.com/album/5QidoXIJCQIRQjOYle9f7m?si=C_pdvXkRTTC2pGf0u6Acbg",
    # אמן חדש
    "https://open.spotify.com/artist/1MyVqiOTfhfsN99ke0rd8g?si=375EHm7FSnaRwgP3jfdBbA"
]

def extract_id_from_url(url):
    """מוציא את המזהה של השיר, האלבום או האמן מה-URL של ספוטיפיי"""
    match = re.search(r'(track|album|artist)/([a-zA-Z0-9]+)', url)
    if match:
        return match.groups() # מחזיר (סוג, מזהה) למשל ('track', '4EhADW...')
    return None, None

def get_track_details(sp, track_id):
    """אוסף פרטים על שיר ספציפי"""
    try:
        track_info = sp.track(track_id)
        if not track_info:
            print(f"Could not retrieve track_info for track ID {track_id}")
            return None
        album_info = sp.album(track_info['album']['id'])
        if not album_info:
            print(f"Could not retrieve album_info for album ID {track_info['album']['id']} (track ID {track_id})")
            return None # Or handle differently, e.g., by returning partial data

        artist_name = ', '.join([artist['name'] for artist in track_info['artists']])
        song_name = track_info['name']
        
        release_date = album_info.get('release_date', '')
        if album_info.get('release_date_precision') == 'year':
            release_date = f"{release_date}-01-01"
        elif album_info.get('release_date_precision') == 'month':
            release_date = f"{release_date}-01"

        album_name = track_info['album']['name']
        
        upc = album_info.get('external_ids', {}).get('upc', '')
        isrc = track_info.get('external_ids', {}).get('isrc', '')
        
        spotify_link = track_info['external_urls'].get('spotify', '')

        return {
            "שם אמן": artist_name,
            "שם השיר": song_name,
            "תאריך שחרור מקורי": release_date,
            "שם אלבום": album_name,
            "UPC": upc,
            "ISRC": isrc,
            "לינק לשיר בספוטיפיי": spotify_link,
            "קרדיט הפקה": "",
            "קרדיט כתיבה": "",
            "לינק להורדה של ה.wav באיכות 44.1khz": "",
            "לינק לארט בגודל 3000x3000": "",
            "לינק לשיר באפל מיוזיק": "",
            "קובץ מילים וקרדיטים (לא חובה)": ""
        }
    except Exception as e:
        print(f"Error fetching details for track ID {track_id}: {e}")
        return None

def generate_spotify_catalog(client_id, client_secret, urls_to_process):
    """Generates a Spotify catalog Excel file from a list of URLs.

    Args:
        client_id (str): Spotify API Client ID.
        client_secret (str): Spotify API Client Secret.
        urls_to_process (list): A list of Spotify track, album, or artist URLs.

    Returns:
        bytes: The content of the generated Excel file as bytes, or None if an error occurs.
    """
    if not client_id or not client_secret:
        print("שגיאה: יש לספק Client ID ו-Client Secret של Spotify.")
        # Consider raising an exception or returning a specific error indicator for Streamlit
        return None

    # אימות והקמת אובייקט Spotify
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    except Exception as e:
        print(f"Error setting up Spotify API: {e}")
        # Consider logging this error for Streamlit to potentially display
        return None

    all_tracks_data = []
    processed_albums = set()  # למניעת עיבוד כפול של אלבומים מאותו אמן
    processed_tracks_isrc = set() # למניעת עיבוד כפול של שירים עם אותו ISRC
    processed_tracks_details = set() # למניעת עיבוד כפול של שירים (אמן,שם,אלבום)

    print(f"מתחיל לעבד {len(urls_to_process)} קישורים...")

    for url in urls_to_process:
        item_type, item_id = extract_id_from_url(url)
        
        if not item_id:
            print(f"Could not extract ID from URL: {url}")
            continue

        print(f"\nProcessing URL: {url} (Type: {item_type}, ID: {item_id})")

        if item_type == 'track':
            print(f"Fetching details for track: {item_id}")
            track_data = get_track_details(sp, item_id)
            if track_data:
                all_tracks_data.append(track_data)
            time.sleep(0.2) # Be polite to the API
        
        elif item_type == 'album':
            print(f"Fetching tracks from album: {item_id}")
            try:
                results = sp.album_tracks(item_id, limit=50)
                album_tracks = results['items']
                while results['next']:
                    time.sleep(0.2)
                    results = sp.next(results)
                    album_tracks.extend(results['items'])
                
                for i, track in enumerate(album_tracks):
                    print(f"  Fetching details for track ID: {track['id']} (Track {i+1}/{len(album_tracks)} from album {item_id})")
                    track_data = get_track_details(sp, track['id'])
                    if track_data:
                        all_tracks_data.append(track_data)
                    time.sleep(0.2)
            except Exception as e:
                print(f"Error fetching tracks for album ID {item_id}: {e}")

        elif item_type == 'artist':
            print(f"Fetching albums for artist: {item_id}")
            try:
                artist_albums_results = sp.artist_albums(item_id, album_type='album,single', limit=50)
                artist_albums_items = artist_albums_results['items']
                while artist_albums_results['next']:
                    time.sleep(0.2)
                    artist_albums_results = sp.next(artist_albums_results)
                    artist_albums_items.extend(artist_albums_results['items'])
                
                print(f"Found {len(artist_albums_items)} albums/singles for artist {item_id}.")
                for i, album in enumerate(artist_albums_items):
                    album_id = album['id']
                    if album_id in processed_albums: # Avoids re-fetching if album listed multiple times under artist (e.g. different markets)
                        print(f"  Skipping already processed album ID: {album_id} (Album {i+1}/{len(artist_albums_items)})")
                        continue
                    
                    print(f"  Fetching tracks from album ID: {album_id} (Album {i+1}/{len(artist_albums_items)} by artist {item_id})")
                    try:
                        album_track_results = sp.album_tracks(album_id, limit=50)
                        album_tracks = album_track_results['items']
                        while album_track_results['next']:
                            time.sleep(0.2)
                            album_track_results = sp.next(album_track_results)
                            album_tracks.extend(album_track_results['items'])
                        
                        print(f"    Found {len(album_tracks)} tracks in album {album_id}.")
                        for j, track in enumerate(album_tracks):
                            print(f"      Fetching details for track ID: {track['id']} (Track {j+1}/{len(album_tracks)} from album {album_id})")
                            track_data = get_track_details(sp, track['id'])
                            if track_data:
                                all_tracks_data.append(track_data)
                            time.sleep(0.2)
                        processed_albums.add(album_id)
                    except Exception as e_album_tracks:
                        print(f"    Error fetching tracks for album {album_id} (Artist {item_id}): {e_album_tracks}")    
                    time.sleep(0.2) # Delay between processing albums of an artist
            except Exception as e_artist_albums:
                print(f"Error fetching albums for artist ID {item_id}: {e_artist_albums}")
        else:
            print(f"Unknown item type '{item_type}' for URL: {url}")

    if not all_tracks_data:
        print("No track data collected. Exiting.")
        return

    df = pd.DataFrame(all_tracks_data)
    # Remove duplicate rows based on ISRC or (Artist, Song Name, Album Name) if ISRC is missing
    df.drop_duplicates(subset=['ISRC'], keep='first', inplace=True)
    df.drop_duplicates(subset=['שם אמן', 'שם השיר', 'שם אלבום'], keep='first', inplace=True)
    
    column_order = [
        "שם אמן", "שם השיר", "תאריך שחרור מקורי", "שם אלבום", 
        "UPC", "ISRC", "לינק לשיר בספוטיפיי",
        "קרדיט הפקה", "קרדיט כתיבה", 
        "לינק להורדה של ה.wav באיכות 44.1khz", "לינק לארט בגודל 3000x3000",
        "לינק לשיר באפל מיוזיק", "קובץ מילים וקרדיטים (לא חובה)"
    ]
    # Ensure all columns exist, add if missing (e.g., if all_tracks_data was empty or had varied structure)
    for col in column_order:
        if col not in df.columns:
            df[col] = ""
            
    df = df[column_order]

    try:
        # במקום לשמור לקובץ, נשמור ל-BytesIO object כדי להחזיר את התוכן
        output_excel_stream = BytesIO()
        df.to_excel(output_excel_stream, index=False, engine='openpyxl')
        output_excel_stream.seek(0) # החזר את הסמן לתחילת ה-stream
        
        print(f"\nהנתונים עובדו בהצלחה.")
        print(f"נמצאו ונוספו {len(df)} שירים ייחודיים.")
        return output_excel_stream.getvalue()
    except Exception as e:
        print(f"Error creating Excel file in memory: {e}")
        # Consider logging this error for Streamlit to potentially display
        return None

# The main execution block is commented out to prevent direct execution when imported.
# If you need to run this script directly for testing, you can uncomment it and 
# provide the necessary API keys and URLs.
# 
# if __name__ == '__main__':
#     # --- הגדרות להרצה ישירה (לצורכי בדיקה בלבד) ---
#     TEST_SPOTIPY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID_HERE' 
#     TEST_SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET_HERE'
#     TEST_URLS = [
#         "https://open.spotify.com/track/4EhADWdV6hJgsuLR8yu3e2?si=7a54365467894d88",
#         # ... add more test URLs if needed
#     ]
# 
#     if TEST_SPOTIPY_CLIENT_ID == 'YOUR_SPOTIFY_CLIENT_ID_HERE' or \
#        TEST_SPOTIPY_CLIENT_SECRET == 'YOUR_SPOTIFY_CLIENT_SECRET_HERE':
#         print("שגיאה: להרצה ישירה, יש להגדיר TEST_SPOTIPY_CLIENT_ID ו-TEST_SPOTIPY_CLIENT_SECRET בקוד.")
#     else:
#         excel_bytes = generate_spotify_catalog(TEST_SPOTIPY_CLIENT_ID, TEST_SPOTIPY_CLIENT_SECRET, TEST_URLS)
#         if excel_bytes:
#             with open('spotify_catalog_direct_test.xlsx', 'wb') as f:
#                 f.write(excel_bytes)
#             print("קובץ אקסל לדוגמה נשמר כ-spotify_catalog_direct_test.xlsx")
#         else:
#             print("לא נוצר קובץ אקסל עקב שגיאות.")
