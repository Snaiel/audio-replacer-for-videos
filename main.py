from moviepy.editor import VideoFileClip, AudioFileClip
from os import listdir, getcwd
from os.path import isfile, join
from tabulate import tabulate

def print_media(media_files):
    data = []

    for i in range(len(media_files)):
        data.append([i, media_files[i]])

    print(tabulate(data, headers=['Index', 'File Name']))

def main():

    media_path = getcwd() + '\\media'
    media_files = [f for f in listdir(media_path)[1:] if isfile(join(media_path, f))]

    print_media(media_files)

    lesson = input('select the original lesson (enter Index): ')
    new_audio_name = input('select the new audio: ')
    final_lesson_name = input('set name of final file (default .mp4): ')

    if len(final_lesson_name.split('.')) == 1:
        final_lesson_name += '.mp4'

    print(final_lesson_name)

    lesson = VideoFileClip('media/' + media_files[int(lesson)])

    new_audio = AudioFileClip('media/' + media_files[int(new_audio_name)])
    new_clip = lesson.set_audio(new_audio)
    new_clip.write_videofile('media/' + final_lesson_name)

if __name__ == "__main__":
    main()