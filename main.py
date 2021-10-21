from moviepy.editor import *

def main():

    lesson_name = input('name of video file: ')
    new_audio_name = input('name of new audio file: ')
    final_lesson_name = input('set name of final file: ')

    lesson = VideoFileClip(lesson_name)

    new_audio = AudioFileClip(new_audio_name)
    new_clip = lesson.set_audio(new_audio)
    new_clip.write_videofile(final_lesson_name)

if __name__ == "__main__":
    main()