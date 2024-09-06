import os

def download_video(url):
    os.system(f'yt-dlp -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]" -o temp_vid --merge-output-format mp4 "{url}"')

def remove_video():
    os.system("rm temp_vid.mp4")