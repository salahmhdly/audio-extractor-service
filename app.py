import subprocess

def extract_audio(video_path, audio_path):
    try:
        command = f"ffmpeg -i {video_path} -vn -acodec libmp3lame -q:a 2 {audio_path}"
        subprocess.run(command, shell=True, check=True)
        print(f"تم فصل الصوت بنجاح وحفظه في: {audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"حدث خطأ أثناء تنفيذ FFmpeg: {e}")
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    video_file = "test_video.mp4"
    audio_file = "output.mp3"
    extract_audio(video_file, audio_file)


