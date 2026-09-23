import os
import random
import subprocess
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def download_youtube_audio(channel_url, duration=60):
    print(f"--> [Source 1] Trying YouTube Channel: {channel_url}")
    cmd_get_ids = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "id",
        "--playlist-end", "20",
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

def download_website_audio(website_url, duration=60):
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
    print("Fetching High-Quality Vertical Image from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    
    keywords = ["nature monk statue", "buddha statue", "meditation nature", "forest sunrise", "mountain landscape portrait"]
    selected_query = random.choice(keywords)
    
    url = f"https://api.pexels.com/v1/search?query={selected_query}&orientation=portrait&per_page=30"
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
    print("Rendering 2K Vertical Video (1440x2560) with FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", "background.jpg",
        "-i", "audio.mp3",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1440:2560:force_original_aspect_ratio=increase,crop=1440:2560",
        "-shortest", "output.mp4"
    ]
    subprocess.run(cmd, check=True)

def send_to_telegram(video_number):
    print("Sending 2K Video & Hashtags to Telegram...")
    
    captions = [
        f"☸️ တရားတော်တိုများ (အပိုင်း {video_number})\n\nစိတ်၏အေးချမ်းခြင်းကို ရှာဖွေပါ 🙏\n\n#ဓမ္မဒါန #တရားတော် #DhammaTalks #MyanmarDhamma #DhammaQuotes #TikTokMyanmar #Fyp",
        f"☸️ နေ့စဉ် တရားတော်တိုများ (အပိုင်း {video_number})\n\nဓမ္မအသိဖြင့် နေထိုင်ပါ 🙏\n\n#တရားတော်များ #ဓမ္မသံစဉ် #Dhamma #Buddhism #MyanmarBuddhism #ForYou #TikTokUni",
        f"☸️ စိတ်အေးချမ်းစရာ တရားတော်များ (အပိုင်း {video_number})\n\nဓမ္မအိုအေး ရိပ်ခိုပါ 🙏\n\n#ပါမောက္ခချုပ်ဆရာတော် #ဓမ္မရသ #Mindfulness #Buddhist #Viral #FypMyanmar"
    ]
    
    selected_caption = random.choice(captions)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    
    with open("output.mp4", "rb") as video:
        files = {"video": video}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": selected_caption
        }
        requests.post(url, files=files, data=data)

if __name__ == "__main__":
    YOUTUBE_CHANNEL = "https://www.youtube.com/@%E1%80%80%E1%80%BC%E1%80%AC%E1%80%94%E1%80%AE%E1%80%80%E1%80%94%E1%80%BA%E1%80%90%E1%80%9B%E1%80%AC%E1%80%B8%E1%80%90%E1%80%B1%E1%80%AC%E1%80%BA%E1%80%99%E1%80%BB%E1%80%AC%E1%80%B82/videos"
    WEBSITE_URL = "https://www.dhammadownload.com/audioinmyanmar.htm"
    YOUTUBE_CHANNEL = "https://www.youtube.com/@BuddhaDhammaRay/videos"
    YOUTUBE_CHANNEL = "https://www.youtube.com/@DHAMMAChanthar-%E1%80%93%E1%80%99%E1%80%B9%E1%80%99%E1%80%81%E1%80%BB%E1%80%99%E1%80%BA%E1%80%B8%E1%80%9E%E1%80%AC"
    YOUTUBE_CHANNEL = "https://www.youtube.com/@Dharmasofbuddha/videos"
    YOUTUBE_CHANNEL = "https://www.youtube.com/@BuddhaOfficial1991/videos"
    YOUTUBE_CHANNEL = "https://www.youtube.com/@dhammatayartaw2025"
    YOUTUBE_CHANNEL = "https://www.youtube.com/@DhammaMyanmar666/videos"
    
    TOTAL_VIDEOS = 3

    for i in range(1, TOTAL_VIDEOS + 1):
        print(f"\n=================== STARTING VIDEO {i}/{TOTAL_VIDEOS} ===================")
        
        audio_success = False
        try:
            download_youtube_audio(YOUTUBE_CHANNEL, duration=60)
            audio_success = True
        except Exception as e:
            print(f"YouTube Download Failed for Video {i}: {e}")

        if not audio_success:
            try:
                download_website_audio(WEBSITE_URL, duration=60)
                audio_success = True
            except Exception as e:
                print(f"Website Download Failed for Video {i}: {e}")

        if audio_success:
            try:
                fetch_pexels_image()
                create_video()
                send_to_telegram(i)
                print(f"SUCCESS: Video {i} sent successfully!")
            except Exception as e:
                print(f"Error producing Video {i}: {e}")
        else:
            print(f"Could not get audio for Video {i}")

        for temp_file in ["audio.mp3", "background.jpg", "output.mp4"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    print("\n================ ALL 3 VIDEOS COMPLETED! ================")
