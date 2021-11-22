import PySimpleGUI as sg
from os import getcwd

from PySimpleGUI.PySimpleGUI import LISTBOX_SELECT_MODE_SINGLE, TEXT_LOCATION_LEFT

processes = ['add new process']

class Lesson():
    def __init__(self, original_video, new_audio, final_name):
        self.original_video = original_video
        self.new_audio = new_audio
        self.final_name = final_name

    def __str__(self) -> str:
        return self.final_name.split('.')[0]

def create_new_process():
    original_video = values['-ORIGINAL_VIDEO-']
    new_audio = values['-NEW_AUDIO-']
    final_name = values['-FINAL_NAME-']

    if original_video != 'original video' and new_audio != 'edited audio' and final_name != 'final file name':
        if len(values['-FINAL_NAME-'].split('.')) == 1:
            final_name += '.mp4'

        processes.append(Lesson(original_video, new_audio, final_name))

        return 'process added'
    else:
        return 'not complete'


def start_processes():
    for process in processes:
        pass

# GUI Creation

media_path = getcwd() + '/media'

print(media_path)

create_process_form = sg.Column(
    layout=[
        [sg.Input(key='-ORIGINAL_VIDEO-', size=(12,1), default_text='original video', enable_events=True, readonly=True), sg.FileBrowse(button_text='browse', initial_folder=media_path, file_types=[('MP4 Video Files','*.mp4')])],
        [sg.Input(key='-NEW_AUDIO-', size=(12,1), default_text='edited audio', enable_events=True, readonly=True), sg.FileBrowse(button_text='browse', initial_folder=media_path, file_types=[('MP3 Audio Files','*.mp3')])],
        [sg.Input(key='-FINAL_NAME-', pad=((5,5),(20,8)), default_text='final file name')],
        [sg.Button('add process', size=(19, 1))]
    ],
    vertical_alignment='top'
)

process_list = sg.Listbox(
    key='-PROCESS_LIST-',
    select_mode=LISTBOX_SELECT_MODE_SINGLE,
    values=processes,
    size=(15,7),
    enable_events=True
)

progress_bar = sg.Graph(
    key='-PROGRESS_BAR-',
    canvas_size=(590, 35),
    graph_bottom_left=(0,0),
    graph_top_right=(590, 35),
    background_color='#ffffff',
    pad=(5,8)
)

layout = [
    [process_list, create_process_form],
    [sg.Button('start'), progress_bar]
]

window = sg.Window('audio replacer', layout, size=(600,270), finalize=True)

progress_bar.draw_text(text='not started', location=(10, 17), text_location=TEXT_LOCATION_LEFT, font=('Helvetica','10'), color="#696969")

while True:
    event, values = window.read()
    print(event, values)
    if event in (None, sg.WINDOW_CLOSED):
        break

    # Show selected file name
    if event in ('-ORIGINAL_VIDEO-', '-NEW_AUDIO-'):
        if len(values[event].split('.')) != 1:
            window[event].update(values[event].split('/')[-1])

    # Add process
    if event == 'add process':
        message = create_new_process()
        for figure in progress_bar.get_figures_at_location((10,17)):
            progress_bar.delete_figure(figure)
        progress_bar.draw_text(text=message, location=(10, 17), text_location=TEXT_LOCATION_LEFT, font=('Helvetica','10'), color="#696969")
        if message == 'process added':
            window['-PROCESS_LIST-'].update(processes)
        
        
            

window.close()