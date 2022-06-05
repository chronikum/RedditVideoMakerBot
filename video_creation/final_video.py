import os
import sys
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
    CompositeVideoClip,
    TextClip
)
from utils.console import print_step
import multiprocessing


W, H = 1080, 1920

def make_final_video(number_of_clips):
    print_step("Creating the final video...")
    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    background_clip = (
        VideoFileClip("assets/mp4/clip.mp4")
        .without_audio()
        .resize(height=H)
        .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )
    # Gather all audio clips
    audio_clips = []
    audio_clips_used = 0
    audio_clips.insert(0, AudioFileClip(f"assets/mp3/title.mp3"))
    for i in range(0, number_of_clips):
        next_audio_clip = AudioFileClip(f"assets/mp3/{i}.mp3").duration
        combined_length = sum([clip.duration for clip in audio_clips])
        print(f"Current length is {combined_length} seconds")
        if (combined_length + next_audio_clip) > 60:
            print("Combined length would be over a minute, so we break here")
            break
        else:
            print(f"new length is {next_audio_clip} seconds")
            audio_clips_used += 1
            audio_clips.append(AudioFileClip(f"assets/mp3/{i}.mp3"))
    
    if (audio_clips_used == 0):
        print("No audio clips were used, so we break here to try again.")
        os.execv(sys.argv[0], sys.argv)
        return
    
    audio_concat = concatenate_audioclips(audio_clips)
    audio_background = AudioFileClip('background_sound/background.mp3').set_duration(audio_concat.duration)
    new_audioclip = CompositeAudioClip([audio_background])
    audio_composite = CompositeAudioClip([audio_concat, new_audioclip])

    # Gather all images
    image_clips = []
    for i in range(0, audio_clips_used):
        image_clips.append(
            ImageClip(f"assets/png/comment_{i}.png")
            .set_duration(audio_clips[i + 1].duration)
            .set_position("center")
            .resize(width=W - 100),
        )
    image_clips.insert(
        0,
        ImageClip(f"assets/png/title.png")
        .set_duration(audio_clips[0].duration)
        .set_position("center")
        .resize(width=W - 100),
    )
    image_concat = concatenate_videoclips(image_clips).set_position(
        ("center", "center")
    )
    image_concat.audio = audio_composite
    
    title_text_imgage = ImageClip(f"background_sound/background.png").set_duration(5).set_position("top").resize(width=W - 100)

    final = CompositeVideoClip([background_clip, image_concat, title_text_imgage])
    final = final.set_duration(audio_composite.duration) # we set the video length to the length of the audio
    
    number_of_threads = multiprocessing.cpu_count()
    print("Writing the final video with {} threads...".format(number_of_threads))
    final.write_videofile(
        "assets/final_video.mp4", fps=3, audio_codec="aac", audio_bitrate="192k", threads=number_of_threads, verbose=False
    )

    for i in range(0, number_of_clips):
        pass
