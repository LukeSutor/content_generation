from moviepy.editor import *
from moviepy.video.fx.all import crop
from dotenv import load_dotenv
import random
import math
import os


def get_video(folder):
    '''
    Returns a random video path from a folder of video files
    '''
    videos = os.listdir(folder)
    video = random.sample(videos, 1)

    return video


def create_video(filename, comment=False):
    '''
    Given a post and filename, create a TikTok / Instagram Reels style video.
    '''
    load_dotenv()
    save_path = os.getenv('SAVE_PATH')
    background_folder = os.getenv('BACKGROUND_VIDEO_DIR')

    # Open voiceover and get its length
    voiceover = AudioFileClip(os.path.join(save_path, filename + ".mp3"))
    voiceover_length = voiceover.duration

    # Do the same if a comment exists and concatenate clips
    if comment:
        voiceover_comment = AudioFileClip(os.path.join(save_path, filename + "_comment" + ".mp3"))
        voiceover_comment_length = voiceover_comment.duration
        # add a second of silence between clips
        silent_second = AudioFileClip(os.path.join(save_path, "silent_second.mp3"))
        voiceover = concatenate_audioclips([voiceover, silent_second, voiceover_comment])
        voiceover_length += voiceover_comment_length
    
    # Get a random video and crop it to a random time interval of the audio length
    video_file = os.path.join(background_folder, get_video(background_folder)[0])
    background_clip = VideoFileClip(video_file, audio=False)

    video_length = background_clip.duration
    start_time = math.floor(random.random() * (video_length  - voiceover_length))
    background_clip = background_clip.subclip(start_time, (start_time + voiceover_length + 2))

    # Crop it to be aspect ratio 9x16 for reels content
    x, y = background_clip.size
    width = y * (9/16)
    if width % 2 == 1:
        width += 1
    x1 = math.floor((x / 2) - (width / 2))
    x2 = math.ceil((x / 2) + (width / 2))
    background_clip = crop(background_clip, x1=x1, y1=0, x2=x2, y2=y)
    background_clip = background_clip.resize(height=1920, width=1080)

    # Add reddit post image overlay
    duration = voiceover_length - voiceover_comment_length if comment else voiceover_length
    reddit_post = ImageClip(os.path.join(save_path, filename + ".png")).set_start(0).set_duration(duration + 1).set_pos(("center", "center"))

    # Add reddit comment overlay if it exists
    if comment:
        comment_start_time = duration + 1
        reddit_comment = ImageClip(os.path.join(save_path, filename + "_comment" + ".png")).set_start(comment_start_time).set_duration(voiceover_comment_length + 1).set_pos(("center", "center"))

    # Create the final clip with the voiceover audio
    clips = [background_clip, reddit_post]
    if comment:
        clips.append(reddit_comment)

    final_clip = CompositeVideoClip(clips).set_audio(voiceover)
    final_clip.write_videofile(os.path.join(save_path, filename + ".mp4"), codec='libx264', ffmpeg_params=['-vf', 'format=yuv420p'], preset='ultrafast')

    background_clip.close()
    reddit_post.close()
    if comment:
        reddit_comment.close()
    final_clip.close()


if __name__ == "__main__":
    create_video('test_video', './gaming_videos')