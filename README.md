# Spotify Catalog Extractor and Enricher

This project provides tools to extract detailed song metadata from Spotify and optionally enrich it with Apple Music links.

## Project Goal

The main goal is to help users (e.g., artists, labels) easily collect comprehensive data about their music catalog from Spotify. This data can be used for various purposes, such as transferring catalog information to a new distributor, internal record-keeping, or analysis.

The output is an Excel file containing details like artist name, song name, release date, album name, UPC, ISRC, Spotify links, and (if enriched) Apple Music links.

## Features

-   **Spotify Data Extraction**: Fetches detailed track, album, and artist information using the Spotify API.
-   **Handles Various Link Types**: Can process individual track links, album links, and artist links (fetching all their tracks).
-   **Duplicate Prevention**: Avoids adding duplicate tracks based on ISRC or a combination of artist, song, and album name.
-   **Excel Output**: Saves all collected data into a well-structured Excel file.
-   **User-Friendly Web Interface**: A Streamlit application (`app.py`) allows users to input API keys and Spotify URLs through a graphical interface and download the results.
-   **Apple Music Link Enrichment (Optional)**: A separate script (`apple_music_linker.py`) can take the generated Excel file and add Apple Music links for each track using the Songlink/Odesli API.

## Setup and Installation

**Prerequisites:**

1.  **Python 3.x installed.** (You can download it from [python.org](https://www.python.org/))
2.  **Spotify API Credentials:**
    *   You need a Spotify Developer account. If you don't have one, create it at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
    *   Create an app in the dashboard to get your **Client ID** and **Client Secret**.

**Installation Steps:**

1.  **Clone or download this project** to your local machine.
2.  **Navigate to the project directory** in your terminal or command prompt:
    ```bash
    cd path/to/spotify-taker-project
    ```
3.  **Install required Python libraries:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Then install the packages:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `streamlit`, `spotipy`, `pandas`, `openpyxl`, and `requests`.

## How to Use

There are two main ways to use this project: via the command-line script or the web application.

### 1. Using the Command-Line Script (`spotify_scraper.py`)

This method is suitable if you prefer working in the terminal.

**Configuration:**

1.  **Open the `spotify_scraper.py` file** in a text editor.
2.  **Locate the following lines** at the beginning of the script (Note: This step is for direct script execution. If using the Streamlit app, API keys are entered in the UI):
    ```python
    # SPOTIPY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID_HERE' # Will be passed as a parameter
    # SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET_HERE' # Will be passed as a parameter
    ```
    When running the script directly (not via the Streamlit app), you would uncomment these and fill them, or modify the test execution block at the end of the file.
3.  **Prepare your list of Spotify URLs (for direct script execution):**
    If running `spotify_scraper.py` directly, you would modify the `TEST_URLS` list within the `if __name__ == '__main__':` block at the end of the file.
    *Example within the test block:*
    ```python
    # TEST_URLS = [
    #     "https://open.spotify.com/track/your_track_id1",
    #     "https://open.spotify.com/album/your_album_id1",
    #     # Add more URLs as needed
    # ]
    ```

**Running the Script Directly (for testing):**

-   **Execution**: Navigate to the project directory in your terminal and run:
    ```bash
    python spotify_scraper.py
    ```
    (This will execute the test block at the end of `spotify_scraper.py` if uncommented and configured.)
-   **Output**: If the test block is run, it will create a file like `spotify_catalog_direct_test.xlsx`.

### 2. Using the Web Application (`app.py`)

For a more user-friendly experience, use the web application built with Streamlit. This allows you to enter your API keys and Spotify links directly in your browser and download the generated Excel file.

**Prerequisites:**

1.  **Python 3.x installed.**
2.  **Install required libraries:** (If you haven't already done so in the main setup)
    Open your terminal or command prompt and run:
    ```bash
    pip install -r requirements.txt
    ```

**Running the Web Application:**

1.  **Navigate to the project directory** in your terminal:
    ```bash
    cd path/to/spotify-taker-project
    ```
2.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
3.  A new tab should open in your web browser with the application interface.
4.  **Enter your Spotify Client ID and Client Secret** in the sidebar.
5.  **Paste the Spotify URLs** (tracks, albums, or artists - one per line) into the text area.
6.  Click the "🚀 Generate Excel Table" button.
7.  Wait for the processing to complete. A loading spinner will indicate progress.
8.  Once finished, a **download button** will appear, allowing you to save the `spotify_catalog_generated.xlsx` file.


### 3. Adding Apple Music Links (`apple_music_linker.py`)

This script enriches the Excel file generated by `spotify_scraper.py` (or the web app) with links to Apple Music.

-   **Preparation**: Ensure the `spotify_catalog_generated.xlsx` (or your named output from the scraper) exists in the project directory.
-   **Execution**: Navigate to the project directory in your terminal and run:
    ```bash
    python apple_music_linker.py
    ```
-   **Output**: The script will update the Excel file, adding a new column "Apple Music Link" (or similar, depending on script's current implementation) and save it as `spotify_catalog_with_apple_music.xlsx` (or a similar name).

## Project Structure
```
/spotify taker
|-- spotify_scraper.py        # Main script for extracting data from Spotify
|-- apple_music_linker.py     # Script for adding Apple Music links
|-- requirements.txt          # List of required Python libraries
|-- spotify_catalog.xlsx      # Output file with Spotify data
|-- spotify_catalog_enriched.xlsx # (Example name) Output file with Apple Music links
|-- README.md                 # This file
```

## Additional Notes
- **Manual Data Entry**: The `spotify_catalog.xlsx` file contains columns for additional data such as "Credits (Production and Writing)", "WAV Download Link", "Cover Art Link", and "Lyrics". These data should be entered manually in the Excel file after running the scripts.
- **API Usage Limits**: Be mindful of Spotify API usage limits to avoid being blocked. The scripts include short delays between requests, but intensive use may still cause issues.
