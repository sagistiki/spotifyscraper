import pandas as pd
import requests
import time

# --- KONFIGURACJA ---
INPUT_EXCEL_FILE = 'spotify_catalog.xlsx'
OUTPUT_EXCEL_FILE = 'spotify_catalog_with_apple_links.xlsx'
SPOTIFY_LINK_COLUMN = 'לינק לשיר בספוטיפיי'
APPLE_MUSIC_LINK_COLUMN = 'לינק לשיר באפל מיוזיק'
SONGLINK_API_BASE_URL = 'https://api.song.link/v1-alpha.1/links'
# --------------------

def get_apple_music_link(spotify_url):
    """Fetches Apple Music link from Songlink API given a Spotify URL."""
    if not spotify_url or not isinstance(spotify_url, str) or not spotify_url.startswith('http'):
        return None
    
    params = {'url': spotify_url}
    try:
        response = requests.get(SONGLINK_API_BASE_URL, params=params, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        
        # Songlink API returns links for various platforms
        # We need to find the one for Apple Music
        apple_music_url = data.get('linksByPlatform', {}).get('appleMusic', {}).get('url')
        return apple_music_url
    except requests.exceptions.RequestException as e:
        print(f"Error calling Songlink API for {spotify_url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {spotify_url} with Songlink: {e}")
    return None

def main():
    try:
        df = pd.read_excel(INPUT_EXCEL_FILE)
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_EXCEL_FILE}' not found.")
        print(f"Please make sure the file exists in the current directory.")
        return
    except Exception as e:
        print(f"Error reading Excel file '{INPUT_EXCEL_FILE}': {e}")
        return

    if SPOTIFY_LINK_COLUMN not in df.columns:
        print(f"Error: Column '{SPOTIFY_LINK_COLUMN}' not found in the Excel file.")
        return

    # Create the Apple Music column if it doesn't exist, initialized with None or empty string
    if APPLE_MUSIC_LINK_COLUMN not in df.columns:
        df[APPLE_MUSIC_LINK_COLUMN] = None

    print(f"Processing {len(df)} tracks to find Apple Music links...")
    for index, row in df.iterrows():
        spotify_link = row[SPOTIFY_LINK_COLUMN]
        print(f"Processing track {index + 1}/{len(df)}: {spotify_link}")
        
        # Check if Apple Music link already exists and is valid, to avoid reprocessing
        existing_apple_link = row.get(APPLE_MUSIC_LINK_COLUMN)
        if pd.notna(existing_apple_link) and isinstance(existing_apple_link, str) and existing_apple_link.startswith('http'):
            print(f"  Skipping, Apple Music link already exists: {existing_apple_link}")
            continue
            
        apple_link = get_apple_music_link(spotify_link)
        if apple_link:
            df.loc[index, APPLE_MUSIC_LINK_COLUMN] = apple_link
            print(f"  Found Apple Music link: {apple_link}")
        else:
            print(f"  Apple Music link not found.")
            df.loc[index, APPLE_MUSIC_LINK_COLUMN] = "" # Or None, depending on preference
        
        time.sleep(0.5) # Being polite to the API, add a small delay

    try:
        df.to_excel(OUTPUT_EXCEL_FILE, index=False, engine='openpyxl')
        print(f"\nProcessing complete. Updated data saved to: {OUTPUT_EXCEL_FILE}")
        print(f"The updated file is located in the current directory as: {OUTPUT_EXCEL_FILE}")
    except Exception as e:
        print(f"Error saving data to Excel file '{OUTPUT_EXCEL_FILE}': {e}")

if __name__ == '__main__':
    main()
