import os
import random
import subprocess
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def get_audio_from_youtube(channel_url, duration=60):
    print(f"--> [Source 1] Trying YouTube Channel: {channel_url}")
    cmd_get_ids = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "id",
        "--playlist-end", "10",
        channel_url
    ]
    result = subprocess.run(cmd_get_ids, capture_output=True, text=True, check=True)
    video_ids = [vid.strip() for vid in result.stdout.split("\n") if vid.strip()]
    
    if not video_ids:
        raise Exception("No videos found in YouTube Channel")

    selected_id = random.choice(video_ids)
    video_url = f"https://www.youtube.com/watch?v={selected_id}"
    print(f"Selected YouTube Video: {video_url}")

    dl_cmd = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "--postprocessor-args", f"ffmpeg:-ss 00:01:00 -t {duration}",
        "-o", "audio.mp3",
        video_url
    ]
    subprocess.run(dl_cmd, check=True)
    print("Successfully fetched audio from YouTube!")

def get_audio_from_website(website_url, duration=60):
    print(f"--> [Source 2] Trying Website MP3: {website_url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(website_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    mp3_links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.endswith(".mp3"):
            full_url = href if href.startswith("http") else website_url.rstrip('/') + '/' + href.lstrip('/')
            mp3_links.append(full_url)

    if not mp3_links:
        raise Exception("No MP3 links found on website")

    selected_mp3 = random.choice(mp3_links)
    print(f"Downloading MP3 from Website: {selected_mp3}")

    mp3_bytes = requests.get(selected_mp3, headers=headers).content
    with open("temp_raw.mp3", "wb") as f:
        f.write(mp3_bytes)

    cmd_cut = [
        "ffmpeg", "-y",
        "-i", "temp_raw.mp3",
        "-ss", "00:00:30",
        "-t", str(duration),
        "-c:a", "libmp3lame",
        "audio.mp3"
    ]
    subprocess.run(cmd_cut, check=True)
    if os.path.exists("temp_raw.mp3"):
        os.remove("temp_raw.mp3")
    print("Successfully fetched audio from Website!")

def fetch_pexels_image():
    print("Fetching Vertical Image from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search?query=nature+monk+statue&orientation=portrait&per_page=20"
    res = requests.get(url, headers=headers).json()
    photos = res.get("photos", [])
    if photos:
        img_url = random.choice(photos)["src"]["large2x"]
        img_data = requests.get(img_url).content
        with open("background.jpg", "wb") as f:
            f.write(img_data)
    else:
        raise Exception("Failed to fetch image from Pexels")

def create_video():
    print("Rendering 9:16 Video with FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", "background.jpg",
        "-i", "audio.mp3",
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "1920k",
        "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-shortest", "output.mp4"
    ]
    subprocess.run(cmd, check=True)

def send_to_telegram():
    print("Sending Video to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open("output.mp4", "rb") as video:
        files = {"video": video}
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": "ပါမောက္ခချုပ်ဆရာတော်၏ တရားတော် တိုများ (Daily Auto Video)"}
        requests.post(url, files=files, data=data)

if __name__ == "__main__":
    YOUTUBE_CHANNEL = "https://www.youtube.com/@DhammaTalks/videos"
    WEBSITE_URL = "https://www.dhammadownload.com"

    audio_success = False

    try:
        get_audio_from_youtube(YOUTUBE_CHANNEL, duration=60)
        audio_success = True
    except Exception as e:
        print(f"YouTube Source Failed: {e}")

    if not audio_success:
        try:
            get_audio_from_website(WEBSITE_URL, duration=60)
            audio_success = True
        except Exception as e:
            print(f"Website Source Failed: {e}")

    if audio_success:
        fetch_pexels_image()
        create_video()
        send_to_telegram()
        print("Workflow Completed Successfully!")
    else:
        print("Error: Both sources failed to provide audio.")
