from fastapi import FastAPI
from routes import router
from ani_api import get_episode_url, get_video_id
from downloader import download_m3u8

app = FastAPI()
app.include_router(router)

def main():
	video_id = get_video_id("https://aniwatchtv.to/watch/your-lie-in-april-31?ep=936")
	video_url, _ = get_episode_url(video_id)
	output_path = "output2.mp4"
	download_m3u8(video_url, output_path, start_time="00:02:00", end_time="00:04:00")

if __name__ == "__main__":
	main()
