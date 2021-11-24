import PySimpleGUI as sg
from moviepy.editor import VideoFileClip, AudioFileClip
from os import getcwd
from threading import Thread
from proglog import TqdmProgressBarLogger

processes = ['add new process']

class Lesson():
    def __init__(self, original_video, new_audio, final_name):
        self.original_video = original_video
        self.new_audio = new_audio
        self.final_name = final_name

    def __str__(self) -> str:
        return self.final_name.split('.')[0]

def check_if_process_exists():
    for process in processes[1:]:
        if values['-FINAL_NAME-'] == str(process):
            return True
    else:
        return False

def create_new_process():
    original_video = values['-ORIGINAL_VIDEO-']
    new_audio = values['-NEW_AUDIO-']
    final_name = values['-FINAL_NAME-']

    if check_if_process_exists() == True:
        return 'duplicate names not allowed'

    if original_video != 'original video' and new_audio != 'edited audio' and final_name != 'final file name':
        if len(values['-FINAL_NAME-'].split('.')) == 1:
            final_name += '.mp4'

        processes.append(Lesson(original_video, new_audio, final_name))

        return 'process added'
    else:
        return 'not complete'


def start_processes():
    toggle_disable_elements()
    for process in processes[1:]:
        my_logger = MyBarLogger(str(process))

        lesson = VideoFileClip('media/' + process.original_video)
        new_audio = AudioFileClip('media/' + process.new_audio)
        new_clip = lesson.set_audio(new_audio)
        new_clip.write_videofile('media/' + process.final_name, logger=my_logger)
    toggle_disable_elements(False)

# Class that accesses the MoviePy progress bar to display it using the PySimpleGUI Graph
class MyBarLogger(TqdmProgressBarLogger):

    def __init__(self, name):
        self.pre_render = False
        self.rendering = False
        self.name = name
        super().__init__()

    def callback(self, **changes):
        # Every time the logger is updated, this function is called
        if len(self.bars):
            print(self.bars)
            for figure in progress_bar.get_figures_at_location((0,35)):
                progress_bar.delete_figure(figure)

            percentage = next(reversed(self.bars.items()))[1]['index'] / next(reversed(self.bars.items()))[1]['total']

            length = percentage * 470
            progress_bar.send_figure_to_back(progress_bar.draw_rectangle(top_left=(0,35), bottom_right=(length,0), fill_color='#a5e8c0', line_width=0))

            if next(reversed(self.bars.items()))[0] == 'chunk':
                if self.pre_render == False:
                    change_progress_text(f'pre-rendering... ({self.name})')
                    self.pre_render = True
                    self.rendering = False
            else:
                if self.rendering == False:
                    change_progress_text(f'rendering... ({self.name})')
                    self.pre_render = False
                    self.rendering = True




# GUI Creation


def change_input_values(type=None):
    if type == 'reset':
            window['-ORIGINAL_VIDEO-'].update(value='original video')
            window['-NEW_AUDIO-'].update(value='edited audio')
            window['-FINAL_NAME-'].update(value='final file name')
    else:
        window['-ORIGINAL_VIDEO-'].update(value=values['-PROCESS_LIST-'][0].original_video)
        window['-NEW_AUDIO-'].update(value=values['-PROCESS_LIST-'][0].new_audio)
        window['-FINAL_NAME-'].update(value=values['-PROCESS_LIST-'][0].final_name)

def toggle_disable_elements(disabled=True):
    elements = ['-PROCESS_LIST-', '-ORIGINAL_VIDEO-', '-NEW_AUDIO-', '-FINAL_NAME-', '-BROWSE_VIDEO-', '-BROWSE_AUDIO-', '-ADD_PROCESS-', '-START-']
    for element in elements:
        window[element].update(disabled=disabled)

def change_progress_text(message):
    for figure in progress_bar.get_figures_at_location((10,17)):
        progress_bar.delete_figure(figure)
    progress_bar.draw_text(text=message, location=(10, 14), text_location=sg.TEXT_LOCATION_LEFT, font=('Helvetica','10'), color="#696969")

media_path = getcwd() + '/media'

create_process_form = sg.Column(
    layout=[
        [sg.Input(key='-ORIGINAL_VIDEO-', size=(12,1), default_text='original video', enable_events=True, readonly=True), sg.FileBrowse(key='-BROWSE_VIDEO-', button_text='browse', initial_folder=media_path, file_types=[('MP4 Video Files','*.mp4')])],
        [sg.Input(key='-NEW_AUDIO-', size=(12,1), default_text='edited audio', enable_events=True, readonly=True), sg.FileBrowse(key='-BROWSE_AUDIO-', button_text='browse', initial_folder=media_path, file_types=[('MP3 Audio Files','*.mp3')])],
        [sg.Input(key='-FINAL_NAME-', size=(20,1), pad=((5,5),(10,2)), default_text='final file name')],
        [sg.Button(key='-ADD_PROCESS-', button_text='add process', size=(17, 1))]
    ],
    vertical_alignment='top',
    pad=(8,8),
)

process_list = sg.Listbox(
    key='-PROCESS_LIST-',
    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
    values=processes,
    size=(15,7),
    enable_events=True,
    right_click_menu=['', ['Delete']]
)

progress_bar = sg.Graph(
    key='-PROGRESS_BAR-',
    canvas_size=(245, 25),
    graph_bottom_left=(0,0),
    graph_top_right=(245, 25),
    background_color='#ffffff',
    pad=(5,2)
)

layout = [
    [process_list, create_process_form],
    [sg.Button('start', key='-START-'), progress_bar]
]

window = sg.Window('audio replacer', layout, finalize=True)

change_progress_text('not started')

while True:
    event, values = window.read()
    print(event, values)
    if event in (None, sg.WINDOW_CLOSED):
        break

    # Show selected file name
    if event in ('-ORIGINAL_VIDEO-', '-NEW_AUDIO-'):
        if len(values[event].split('.')) != 1:
            window[event].update(values[event].split('/')[-1])

    # Change values according to selected process
    if event == '-PROCESS_LIST-':
        change_input_values('reset' if values[event][0] == 'add new process' else None)

    # Add process
    if event == '-ADD_PROCESS-':
        message = create_new_process()
        change_progress_text(message)
        if message == 'process added':
            window['-PROCESS_LIST-'].update(processes)
            change_input_values('reset')

    # Delete process
    if event == 'Delete':
        for process in processes[1:]:
            if process == values['-PROCESS_LIST-'][0]:
                processes.remove(process)
        window['-PROCESS_LIST-'].update(processes)
        change_input_values('reset')

    if event == '-START-':
        if len(processes) == 1:
            change_progress_text('no processes')
        else:
            moviepy = Thread(target=start_processes)
            moviepy.start()

window.close()