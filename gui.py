import PySimpleGUI as sg
from moviepy.editor import VideoFileClip, AudioFileClip
from os import getcwd
from multiprocessing import Process, Queue, Pipe
from proglog import TqdmProgressBarLogger
from time import sleep

class Video():
    def __init__(self, original_video, new_audio, final_name):
        self.original_video = original_video
        self.new_audio = new_audio
        self.final_name = final_name

    def __str__(self) -> str:
        return self.final_name.split('.')[0]

    def __getstate__(self):
        return self.__dict__
        
    def __setstate__(self, d):
        self.__dict__ = d

def pysimplegui_process(interface_parameters, video_processes, pipe_pysimplegui):
    processes = ['add new process']

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
        for figure in progress_bar.get_figures_at_location(interface_parameters['progress_bar_text_pos']):
            progress_bar.delete_figure(figure)
        progress_bar.draw_text(text=message, location=interface_parameters['progress_bar_text_pos'], text_location=sg.TEXT_LOCATION_LEFT, font=('Helvetica','10'), color="#696969")
        
    def progress_bar_updater(percentage, progress_text_id=None):
        for figure in progress_bar.get_figures_at_location((0,interface_parameters['progress_bar_size'][1])):
            progress_bar.delete_figure(figure)
        if percentage == 0:
            for figure in progress_bar.get_figures_at_location(interface_parameters['progress_bar_text_pos']):
                progress_text_id = figure
            if progress_text_id:
                progress_text = progress_bar.tk_canvas.itemcget(progress_text_id, 'text')
                progress_bar.erase()
                change_progress_text(progress_text)
            else:
                progress_bar.erase()
            
        length = percentage * interface_parameters['progress_bar_size'][0]
        progress_bar.send_figure_to_back(progress_bar.draw_rectangle(top_left=(0,interface_parameters['progress_bar_size'][1]), bottom_right=(length,0), fill_color='#a5e8c0', line_width=0))

    media_path = getcwd() + '/media'

    create_process_form = sg.Column(
        layout=[
            [sg.Input(key='-ORIGINAL_VIDEO-', size=(12,1), default_text='original video', enable_events=True, readonly=True, use_readonly_for_disable=True), sg.FileBrowse(key='-BROWSE_VIDEO-', button_text='browse', initial_folder=media_path, file_types=[('MP4 Video Files','*.mp4')])],
            [sg.Input(key='-NEW_AUDIO-', size=(12,1), default_text='edited audio', enable_events=True, readonly=True, use_readonly_for_disable=True), sg.FileBrowse(key='-BROWSE_AUDIO-', button_text='browse', initial_folder=media_path, file_types=[('MP3 Audio Files','*.mp3')])],
            [sg.Input(key='-FINAL_NAME-', size=interface_parameters['final_name_input_size'], pad=interface_parameters['final_name_input_pad'], default_text='final file name')],
            [sg.Button(key='-ADD_PROCESS-', button_text='add process', size=interface_parameters['add_process_button_size'])]
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
        canvas_size=interface_parameters['progress_bar_size'],
        graph_bottom_left=(0,0),
        graph_top_right=interface_parameters['progress_bar_size'],
        background_color='#ffffff',
        pad=interface_parameters['progress_bar_pad']
    )

    layout = [
        [process_list, create_process_form],
        [sg.Button('start', key='-START-'), progress_bar]
    ]

    window = sg.Window('audio replacer', layout, finalize=True)

    change_progress_text('not started')

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

            video = Video(original_video, new_audio, final_name)

            processes.append(video)

            return f'process added: {video}'
        else:
            return f'not complete'

    moviepy_running = False

    while True:
        event, values = window.read(timeout=20)

        if pipe_pysimplegui.poll():
            item = pipe_pysimplegui.recv()
            # print(item)
            if item == 'finished':
                progress_bar_updater(0)
                change_progress_text('finished queue')
                processes = ['add new process']
                toggle_disable_elements(False)
                window['-PROCESS_LIST-'].update(processes)
                moviepy_running = False
            elif item == 'started':
                moviepy_running = True
            elif item == 'wait':
                moviepy_running = False
                # progress_bar_updater(1)
            elif isinstance(item, float):
                progress_bar_updater(item)
            else:
                # print(item)
                progress_bar_updater(0)
                change_progress_text(item)

        if moviepy_running:
            pipe_pysimplegui.send('give me data')

        if event != '__TIMEOUT__':
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
            if 'process added' in message:
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
                toggle_disable_elements()
                change_progress_text('started...')

                window.refresh()

                for process in processes[1:]:
                    video_processes.put(process)

                pipe_pysimplegui.send('start')
    window.close()
    pipe_pysimplegui.send('close')

def moviepy_process(video_processes, pipe_moviepy):

    def start_processes():
        while not video_processes.empty():
            process = video_processes.get()
            my_logger = MyBarLogger(str(process))

            lesson = VideoFileClip('media/' + process.original_video)
            new_audio = AudioFileClip('media/' + process.new_audio)
            new_clip = lesson.set_audio(new_audio)
            new_clip.write_videofile('media/' + process.final_name, logger=my_logger)
        pipe_moviepy.send('finished')

    # Class that accesses the MoviePy progress bar to display it using the PySimpleGUI Graph
    class MyBarLogger(TqdmProgressBarLogger):

        def __init__(self, name):
            self.pre_render = False
            self.rendering = False
            self.started = False
            self.name = name
            super().__init__()

        def callback(self, **changes):
            # Every time the logger is updated, this function is called
            if len(self.bars):
                if self.started is False:
                    pipe_moviepy.send('started')
                    self.started = True

                if pipe_moviepy.poll() and pipe_moviepy.recv() == 'give me data':
                    #print(self.bars)

                    if next(reversed(self.bars.items()))[0] == 'chunk':
                        if self.pre_render == False:
                            # change_progress_text(f'pre-rendering... ({self.name})')
                            pipe_moviepy.send(f'pre-rendering... ({self.name})')
                            self.pre_render = True
                            self.rendering = False
                            return
                    else:
                        if self.rendering == False:
                            # change_progress_text(f'rendering... ({self.name})')
                            pipe_moviepy.send(f'rendering... ({self.name})')
                            self.pre_render = False
                            self.rendering = True 
                            return

                    percentage = next(reversed(self.bars.items()))[1]['index'] / next(reversed(self.bars.items()))[1]['total']

                    if percentage < 0:
                        percentage = 0

                    if percentage > 1:
                        percentage = 1

                    if round(percentage, 2) == 1:
                        self.started = False
                        pipe_moviepy.send('wait')

                    pipe_moviepy.send(percentage)


    while True:
        item = pipe_moviepy.recv()
        if item == 'start':
            start_processes()
        elif item == 'close':
            break


def main():
    video_processes = Queue()

    pipe_pysimplegui, pipe_moviepy = Pipe(duplex=True)

    p_pysimplegui = Process(target=pysimplegui_process, args=(interface_parameters, video_processes, pipe_pysimplegui))
    p_moviepy = Process(target=moviepy_process, args=(video_processes, pipe_moviepy))

    p_pysimplegui.start()
    p_moviepy.start()

    while True:
        if p_pysimplegui.is_alive() and p_moviepy.is_alive():
            pass
        else:
            p_pysimplegui.terminate()
            p_moviepy.terminate()
            return


if __name__ == '__main__':
    interface_parameters = {
        'media_input_size': (12,1),
        'final_name_input_size': (20,1),
        'final_name_input_pad': ((5,5),(10,2)),
        'add_process_button_size': (17, 1),
        'progress_bar_size': (245, 25),
        'progress_bar_text_pos': (10, 14),
        'progress_bar_pad': (5,2)
    }
    main()