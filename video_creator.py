import os
import math
import random
from moviepy.editor import *
from moviepy.video.fx.all import crop


def get_video(folder):
    '''
    Returns a random video path from a folder of video files
    '''
    videos = os.listdir(folder)
    
    video = random.sample(videos, 1)

    return video


def create_video(filename, background_folder):
    '''
    Given a post and filename, create a TikTok / Instagram Reels style video.
    '''
    # Open voiceover and get its length
    voiceover = AudioFileClip(filename + ".mp3")
    voiceover_length = voiceover.duration
    
    # Get a random video and crop it to a random time interval of the audio length
    video_file = background_folder + "/" + get_video(background_folder)[0]
    background_clip = VideoFileClip(video_file, audio=False)

    video_length = background_clip.duration
    start_time = math.floor(random.random() * (video_length  - voiceover_length))
    background_clip = background_clip.subclip(start_time, (start_time + voiceover_length))

    # Crop it to be aspect ratio 9x16 for reels content
    x, y = background_clip.size
    width = y * (9/16)
    # if width % 2 == 1:
    #     width += 1
    x1 = math.floor((x / 2) - (width / 2))
    x2 = math.ceil((x / 2) + (width / 2))
    background_clip = crop(background_clip, x1=x1, y1=0, x2=x2, y2=y)
    background_clip = background_clip.resize(height=1920, width=1080)

    # background_clip.write_videofile('testing.mp4')

    # Add reddit post image overlay
    reddit_post = ImageClip(filename + ".png").set_start(0).set_duration(voiceover_length).set_pos(("center", "center"))

    # Create the final clip with the voiceover audio
    final_clip = CompositeVideoClip([background_clip, reddit_post])
    final_clip.audio = voiceover

    final_clip.write_videofile((filename + ".mp4"), codec='libx264', ffmpeg_params=['-vf', 'format=yuv420p'], preset='veryslow') #ffmpeg_params=['-vf', 'format=yuv420p']

    background_clip.close()
    reddit_post.close() # 9347Kb
    final_clip.close()


if __name__ == "__main__":
    create_video('test_video', './gaming_videos')