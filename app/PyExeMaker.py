# -*- mode: python ; coding: utf-8 -*-

from asyncio.windows_events import NULL
import configparser
import json
import os
import re
import string
import subprocess
import sys
import threading
from pathlib import Path

import PySimpleGUI as sg

'''
    Make a "Windows OS" executable with PyInstaller
'''

global last_workspace, appdatadir, homeuserdir

appdir = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.append(appdir)

userdata = os.getenv('LOCALAPPDATA') 
homeuserdir = os.path.expanduser('~')
filename = os.path.splitext(os.path.split(__file__)[1])[0]
appdatadir = os.path.join(userdata, filename)

import resources
from app import __version__

# move templates to user folder app
if not os.path.exists(f"{appdatadir}\\templates"): 
    import shutil
    shutil.move("./templates", f"{appdatadir}\\templates")

def startup():
    if os.path.exists(f"{appdatadir}/config.ini"):
        config = configparser.ConfigParser()
        config.sections()
        config.read(f"{appdatadir}/config.ini")
        last_workspace = config.get('Path', 'last-project') 
    else:
        config = configparser.ConfigParser()
        config['Path'] = {'last-project': ''}
        with open(f'{appdatadir}/config.ini', 'w') as configfile:
            config.write(configfile)
        last_workspace = ''
    return last_workspace


class ExeMaker():
    def __init__(self):
        sg.theme('DarkGrey6')

        tab_version = [ 
                            [sg.Text(' ')],
                            [sg.Text(' ')],
                            [sg.Text(' ')],
            [sg.T('Version Number:', size=(15, 1)),
             sg.Input(key='vermajor0', size=(2, 1), enable_events=True),
             sg.Input(key='vermajor1', size=(2, 1), enable_events=True),
             sg.Input(key='verminor0', size=(2, 1), enable_events=True)],
            [sg.T('CompanyName:', size=(15, 1)),
             sg.Input(key='CompanyName', size=(20, 1))],
            [sg.T('FileDescription:', size=(15, 1)),
             sg.Input(key='FileDescription', size=(20, 1))],
            [sg.T('InternalName:', size=(15, 1)),
             sg.Input(key='InternalName', size=(20, 1))],
            [sg.T('LegalCopyright:', size=(15, 1)),
             sg.Input(key='LegalCopyright', size=(20, 1))],
            [sg.T('OriginalFilename:', size=(15, 1)),
             sg.Input(key='OriginalFilename', size=(20, 1))],
            [sg.T('ProductName:', size=(15, 1)),
             sg.Input(key='ProductName', size=(20, 1))],
            [sg.T('ProductVersion:', size=(15, 1)),
             sg.Input(key='prodmajor0', size=(2, 1), enable_events=True),
             sg.Input(key='prodmajor1', size=(2, 1), enable_events=True),
             sg.Input(key='prodminor0', size=(2, 1), enable_events=True)],

            ]

        tab_makefile = [
            [sg.Multiline(autoscroll=True, size=(88, 33), enable_events=True,
                          auto_refresh=True, font='Courier 9',
                          key='-MAKE-SPEC-')],
                        ] 

        layout_user = [[
            sg.Frame(title="PyExeMaker", font=("monospace", 14), element_justification='right',
                      layout=[
                          [sg.Button('New Workspace', key='-NEWWRKSPC-'),
                           sg.Button('Load Workspace', key='-LOADWRKSPC-'),
                           sg.Button('Save Workspace', key='-SAVEWRKSPC-')],
                          [sg.Text('Virtual Env Path'),
                           sg.Input(key='-pythonpath-', size=(65, 1)),
                           sg.FolderBrowse(initial_folder=homeuserdir)],
                          [sg.Text('Project Folder'),
                           sg.Input(key='-workdir-', size=(65, 1)),
                           sg.FolderBrowse(initial_folder=homeuserdir)], 
                          [sg.Text('Source Python File'),
                           sg.Input(key='-sourcefile-', size=(65, 1)),
                           sg.FileBrowse(file_types=(("Python Files", "*.py"),
                                                     ))],
                          [sg.Text('Icon App'),
                           sg.Input(key='-iconfile-', size=(65, 1)),
                           sg.FileBrowse(
                               file_types=(("Icon Files", "*.ico"),))],
                        [sg.Text(' ')],
                          [sg.Radio('Make Spec ONE FILE', "RADIO1",
                                    default=True, size=(20, 1),
                                    enable_events=True,
                                    key='SPEC-ONEFILE'),
                           sg.Radio('Make Spec FOLDER ', "RADIO1", size=(18, 1),
                                    enable_events=True, key='SPEC-DIR')],
                          [sg.TabGroup([
                              [sg.Tab('Version', tab_version, element_justification='center', disabled=False)],
                              [sg.Tab('MakeSpec', tab_makefile,
                                      disabled=False)]],
                                       enable_events=True, key='-tab-')],
                          [sg.pin(sg.Button('New Version File', 
                                            key='-NEWVERSION-', visible=True)),
                           sg.pin(sg.Button('Populate Version File',
                                            key='-POPVERSION-', visible=True)),
                           sg.pin(sg.Button('Make Version File',
                                            key='-MAKEVERSION-', visible=True)),
                           sg.pin(sg.Button('New SpecFile', key='newspec',
                                            visible=False)),
                           sg.pin(sg.Button('Load SpecFile', key='loadspec',
                                            visible=False)),
                           sg.pin(sg.Button('Save SpecFile', key='savespec',
                                            visible=False)),
                           sg.Button('Make EXE', bind_return_key=True),
                           sg.Button('Quit', size=(5, 1),
                                     button_color=('white', 'firebrick3'))],
                          [sg.StatusBar(
                              text=f'PyInstaller EXE Maker v{__version__}',
                              font='Courier 8', text_color='black',
                              background_color='thistle4', relief=sg.RELIEF_FLAT,
                              justification='right', visible=True)],
                          ]),
             ]]
        layout_terminal = [[
            sg.Frame(title='Terminal', font=("monospace", 14), layout=[
                    [sg.Output(size=(90, 49),  key="_terminal_",
                            #    echo_stdout_stderr=True,  # un(/)coment to view
                               font='Courier 10')],
            ])
        ]]
        col1 = sg.Column(layout_user,
                         size=(675, 848))
        col2 = sg.Column(layout_terminal,
                         size=(800, 848))
        winlayout = [
            [
                col1,
                sg.VSeparator(),
                col2,
            ]
        ]
        self.window = sg.Window('PyInstaller EXE Maker', layout=winlayout, size=(1490, 850),
                                finalize=True, font=("monospace", 9),
                                resizable=False,
                                icon=f'{appdatadir}/resources/'\
                                    'navigatorsimple.ico')
        # col1.expand(True, True)
        # col2.expand(True, True)

    def spec_finder(self):
        from fnmatch import fnmatch
        path = self.window['-workdir-'].get()

        for drive, folders, files in os.walk(path):
            for file in files:
                if not fnmatch(file, '*.spec'):
                    continue
                if file == "spec_folder.spec":
                    self.window['SPEC-DIR'].update(value=True)
                    self.window.write_event_value("loadspec", "")
                elif file == "spec_onefile.spec":
                    self.window['SPEC-ONEFILE'].update(value=True)
                    self.window.write_event_value("loadspec", "")
         
    def start(self):
        while True:

            event, self.values = self.window.read()

            if event in ('Exit', 'Quit', None) or event == sg.WINDOW_CLOSED:
                break
            if event == 'Make EXE':
                if self.values['SPEC-ONEFILE']:
                    command_line = '{}/Scripts/pythonw.exe {}/Scripts/pyinstaller.exe '\
                        '-y {}/{}'.format(self.values['-pythonpath-'],
                                          self.values['-pythonpath-'],
                                          self.values['-workdir-'],
                                          'spec_onefile.spec')
                    print(f"{command_line=}")
                    pass
                else:
                    command_line = '{}/Scripts/pythonw.exe {}/Scripts/pyinstaller.exe '\
                        '-y {}/{}'.format(self.values['-pythonpath-'],
                                            self.values['-pythonpath-'],
                                            self.values['-workdir-'],
                                            'spec_folder.spec')
                    print(f"{command_line=}")
                # sys.exit()
                self.save_workspace()
                try:
                    self.window["_terminal_"].update('')
                    print('Making EXE...the program has NOT locked up...')
                    print('Running command {}'.format(command_line))
                    thread = threading.Thread(target=self.runCommand,
                                              args=(command_line,
                                                    self.window),
                                              daemon=True)
                    thread.start()
                except Exception:
                    sg.PopupError('Something went wrong',
                                  'close this window and copy command \
                                      line from text printed out in main\
                                          window','Here is the output from\
                                          the run')
                    print('Copy and paste this line into the command prompt\
                        to manually run PyInstaller:\n\nPyInstaller is venv installed !?', command_line)
                    return
            elif event == '-NEWVERSION-':
                self.new_versionfile()
            elif event == '-MAKEVERSION-':
                self.make_versionfile()
            elif event == '-POPVERSION-':
                self.populate_versionfile()
            # only input two digits version Number
            if event == 'vermajor0' and self.values['vermajor0']\
            and not re.fullmatch('\d{1,2}', self.values['vermajor0']):
                self.window['vermajor0'].Update('')
            if event == 'vermajor1' and self.values['vermajor1']\
            and not re.fullmatch('\d{1,2}', self.values['vermajor1']):
                self.window['vermajor1'].Update('')
            if event == 'verminor0' and self.values['verminor0']\
            and not re.fullmatch('\d{1,2}', self.values['verminor0']):
                self.window['verminor0'].Update('')
            # only input two digits ProductVersion
            if event == 'prodmajor0' and self.values['prodmajor0']\
            and not re.fullmatch('\d{1,2}', self.values['prodmajor0']):
                self.window['prodmajor0'].Update('')
            if event == 'prodmajor1' and self.values['prodmajor1']\
            and not re.fullmatch('\d{1,2}', self.values['prodmajor1']):
                self.window['prodmajor1'].Update('')
            if event == 'prodminor0' and self.values['prodminor0']\
            and not re.fullmatch('\d{1,2}', self.values['prodminor0']):
                self.window['prodminor0'].Update('')
            if event == 'newspec' and self.values['SPEC-ONEFILE']:
                self.makespecfile("ONEFILE")
            elif event == 'newspec' and not self.values['SPEC-ONEFILE']:
                self.makespecfile(None)
            elif event == 'loadspec' and self.values['SPEC-ONEFILE']:
                try:
                    with open(f"{self.values['-workdir-']}/spec_onefile.spec", 'r')\
                        as file:
                        data = file.read()
                    self.window['-MAKE-SPEC-'].update("")
                    self.window['-MAKE-SPEC-'].Update(data)
                except FileNotFoundError:
                    pass
            elif event == 'loadspec' and self.values['SPEC-DIR']:
                try:
                    with open(f"{self.values['-workdir-']}/spec_folder.spec", 'r')\
                        as file:
                        data = file.read()
                    self.window['-MAKE-SPEC-'].update("")
                    self.window['-MAKE-SPEC-'].Update(data)
                except FileNotFoundError:
                    pass
            elif event == 'savespec' and self.values['SPEC-ONEFILE']:
                try:
                    file = Path(f"{self.values['-workdir-']}/spec_onefile.spec")
                    file.write_text(self.values.get('-MAKE-SPEC-'))
                    self.window["_terminal_"].update('')
                    self.window["_terminal_"].\
                        update(self.values.get('-MAKE-SPEC-'))
                except FileNotFoundError:
                    pass
            elif event == 'savespec' and self.values['SPEC-DIR']:
                try:
                    file = Path(f"{self.values['-workdir-']}/spec_folder.spec")
                    file.write_text(self.values.get('-MAKE-SPEC-'))
                    self.window["_terminal_"].update('')
                    self.window["_terminal_"].\
                        update(self.values.get('-MAKE-SPEC-'))
                except FileNotFoundError:
                    pass
            elif event == '-SAVEWRKSPC-':
                self.save_workspace()
            elif event == '-NEWWRKSPC-':
                self.new_workspace()
            elif event == '-LOADWRKSPC-':
                self.load_workspace("")
            elif event == '-THREADFINISHED-':
                print('*')
                print('**** DONE ****')
            if self.values['-tab-'] == 'Version':
                self.window['-POPVERSION-'].update(visible=True)
                self.window['-MAKEVERSION-'].update(visible=True)
                self.window['-NEWVERSION-'].update(visible=True)
                self.window['newspec'].update(visible=False)
                self.window['loadspec'].update(visible=False)
                self.window['savespec'].update(visible=False)
            else:
                self.window['-POPVERSION-'].update(visible=False)
                self.window['-MAKEVERSION-'].update(visible=False)
                self.window['-NEWVERSION-'].update(visible=False)
                self.window['newspec'].update(visible=True)
                self.window['loadspec'].update(visible=True)
                self.window['savespec'].update(visible=True)

        self.window.refresh()

    def new_workspace(self):
        with open(f"{appdatadir}/templates/template-workspace-project.json",
                  "r") as f:
            loaddatas = json.loads(f.read()) 
        for i, (key, value) in enumerate(loaddatas.items()):
            if key == "filevers":
                self.window['vermajor0']\
                    .Update(value.split(',')[0])
                self.window['vermajor1']\
                    .Update(value.split(',')[1])
                self.window['verminor0']\
                    .Update(value.split(',')[2])
            elif key == "CompanyName":
                self.window['CompanyName'].Update(value)
            elif key == "FileDescription":
                self.window['FileDescription']\
                    .Update(value)
            elif key == "InternalName":
                self.window['InternalName'].Update(value)
            elif key == "LegalCopyright":
                self.window['LegalCopyright'].Update(value)
            elif key == "OriginalFilename":
                self.window['OriginalFilename']\
                    .Update(value)
            elif key == "ProductName":
                self.window['ProductName'].Update(value)
                # self.window['-layoutuser-'].update("New Project")
            elif key == "ProductVersion":
                self.window['prodmajor0']\
                    .Update(value.split('.')[0])
                self.window['prodmajor1']\
                    .Update(value.split('.')[1])
                self.window['prodminor0']\
                    .Update(value.split('.')[2])
            elif key == "workdirectory":
                self.window['-workdir-'].Update(value)
            elif key == "sourcepythonfile":
                self.window['-sourcefile-'].Update(value)
            elif key == "iconfile":
                self.window['-iconfile-'].Update(value)
            elif key == "pythonpath":
                self.window['-pythonpath-'].Update(value)
        self.window['-MAKE-SPEC-'].update("")
        self.window["_terminal_"].update("")

    def save_workspace(self):
        config = configparser.ConfigParser()
        config['Path'] = {'Last-Project': f"{self.values['-workdir-']}"}
        with open(f"{appdatadir}/config.ini", 'w') as configfile:
            config.write(configfile)
        
        # capture all fields
        data = dict(
                    pythonpath = f"{self.values['-pythonpath-']}",
                    workdirectory = f"{self.values['-workdir-']}",
                    sourcepythonfile = f"{self.values['-sourcefile-']}",
                    iconfile = f"{self.values['-iconfile-']}",
                    filevers = f"{self.values['vermajor0']},"\
                        f"{self.values['vermajor1']},"\
                            f"{self.values['verminor0']}",
                    prodvers = f"{self.values['prodmajor0']},"\
                        f"{self.values['prodmajor1']},"\
                            f"{self.values['prodminor0']}",
                    CompanyName = f"{self.values['CompanyName']}",
                    FileDescription = f"{self.values['FileDescription']}",
                    FileVersion = f"{self.values['vermajor0']}."\
                        f"{self.values['vermajor1']}."\
                            f"{self.values['verminor0']}",
                    InternalName = f"{self.values['InternalName']}",
                    LegalCopyright = f"{self.values['LegalCopyright']}",
                    OriginalFilename = f"{self.values['OriginalFilename']}",
                    ProductName = f"{self.values['ProductName']}",
                    ProductVersion = f"{self.values['prodmajor0']}."\
                        f"{self.values['prodmajor1']}."\
                            f"{self.values['prodminor0']}"
                    )
        with open(f"{self.values['-workdir-']}/"\
            "workspace-project.json", "w") as jfile:
            json.dump(data, jfile, indent=4)
            
    def load_workspace(self, path):
        if path:
            if os.path.exists(f"{path}/workspace-project.json"):
                with open(f"{path}/workspace-project.json", "r") as f:
                    loaddatas = json.loads(f.read()) 
                for i, (key, value) in enumerate(loaddatas.items()):
                    if key == "filevers":
                        self.window['vermajor0']\
                            .Update(value.split(',')[0])
                        self.window['vermajor1']\
                            .Update(value.split(',')[1])
                        self.window['verminor0']\
                            .Update(value.split(',')[2])
                    elif key == "CompanyName":
                        self.window['CompanyName'].Update(value)
                    elif key == "FileDescription":
                        self.window['FileDescription']\
                            .Update(value)
                    elif key == "InternalName":
                        self.window['InternalName'].Update(value)
                    elif key == "LegalCopyright":
                        self.window['LegalCopyright'].Update(value)
                    elif key == "OriginalFilename":
                        self.window['OriginalFilename']\
                            .Update(value)
                    elif key == "ProductName":
                        self.window['ProductName'].Update(value)
                        # self.window['-layoutuser-'].Update(value)
                    elif key == "ProductVersion":
                        self.window['prodmajor0']\
                            .Update(value.split('.')[0])
                        self.window['prodmajor1']\
                            .Update(value.split('.')[1])
                        self.window['prodminor0']\
                            .Update(value.split('.')[2])
                    elif key == "workdirectory":
                        self.window['-workdir-'].Update(value)
                    elif key == "sourcepythonfile":
                        self.window['-sourcefile-'].Update(value)
                    elif key == "iconfile":
                        self.window['-iconfile-'].Update(value)
                    elif key == "pythonpath":
                        self.window['-pythonpath-'].Update(value)
                self.spec_finder()
        else:
            path = sg.popup_get_folder('Project Folder ?')
            if os.path.exists(f"{path}/workspace-project.json"):
                with open(f"{path}/workspace-project.json", "r") as f:
                    loaddatas = json.loads(f.read())
                for i, (key, value) in enumerate(loaddatas.items()):
                        if key == "filevers":
                            self.window['vermajor0']\
                                .Update(value.split(',')[0])
                            self.window['vermajor1']\
                                .Update(value.split(',')[1])
                            self.window['verminor0']\
                                .Update(value.split(',')[2])
                        elif key == "CompanyName":
                            self.window['CompanyName'].Update(value)
                        elif key == "FileDescription":
                            self.window['FileDescription']\
                                .Update(value)
                        elif key == "InternalName":
                            self.window['InternalName']\
                                .Update(value)
                        elif key == "LegalCopyright":
                            self.window['LegalCopyright']\
                                .Update(value)
                        elif key == "OriginalFilename":
                            self.window['OriginalFilename']\
                                .Update(value)
                        elif key == "ProductName":
                            self.window['ProductName'].Update(value)
                            # self.window['-layoutuser-'].update(value)
                        elif key == "ProductVersion":
                            self.window['prodmajor0']\
                                .Update(value.split('.')[0])
                            self.window['prodmajor1']\
                                .Update(value.split('.')[1])
                            self.window['prodminor0']\
                                .Update(value.split('.')[2])
                        elif key == "workdirectory":
                            self.window['-workdir-'].Update(value)
                        elif key == "sourcepythonfile":
                            self.window['-sourcefile-']\
                                .Update(value)
                        elif key == "iconfile":
                            self.window['-iconfile-'].Update(value)
                        elif key == "pythonpath":
                            self.window['-pythonpath-']\
                                .Update(value)
                self.spec_finder()
            else:
              print("**** Workspace NOT exist *****")

    def runCommand(self, cmd, window=None):
        """ run shell command

        @param cmd: command to execute
        @param timeout: timeout for command execution

        @return: (return code from command, command output)
        """

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
        output = ''
        for line in p.stdout:
            line = line.decode(errors='replace' if (sys.version_info) < (3, 5)
                            else 'backslashreplace').rstrip()
            output += line
            print(line)
            if window:
                window.refresh()
        window.write_event_value('-THREADFINISHED-', '*** DONE ***')
    
    def makespecfile(self, type):
        # file = os.path.split(f"{self.values['-sourcefile-']}")
        wkdir = self.values['-workdir-']
        nname = os.path.normpath(wkdir)
        name = nname.split(os.sep)[-1]
        srcfile = self.values['-sourcefile-']
        icon = self.values['-iconfile-']
        data = dict(workdir = f"{wkdir}",
                    pythonfile = f"{srcfile}",
                    pythonname = f"{name}",
                    iconfile = f"{icon}",
                    )
        # res = [os.path.exists(i) for i in list((f"{wkdir}/dist", f"{wkdir}/build"))]
        # if not res[0]:
            # os.mkdir(f"{wkdir}\\dist")
        # if not res[1]:
            # os.mkdir(f"{wkdir}\\build")
        if type == "ONEFILE":
            with open(f"{appdatadir}/templates/template-spec_onefile.spec", 'r') as t:
                template = string.Template(t.read())
                new_file = template.substitute(data)
        
            with open(f"{self.values['-workdir-']}/spec_onefile.spec", "w") as output:
                output.write(new_file)

            with open(f"{self.values['-workdir-']}/spec_onefile.spec", 'r') as file:
                data = file.read()
        else:
            with open(f"{appdatadir}/templates/template-spec_folder.spec", 'r') as t:
                template = string.Template(t.read())
                new_file = template.substitute(data)
        
            with open(f"{self.values['-workdir-']}/spec_folder.spec", "w") as output:
                output.write(new_file)

            with open(f"{self.values['-workdir-']}/spec_folder.spec", 'r') as file:
                data = file.read()   
        self.window['-MAKE-SPEC-'].update(data)
        self.window["_terminal_"].update('')
        self.window["_terminal_"].update(data)
            
    def make_versionfile(self):
        # load template txt
        with open(f"{appdatadir}/templates/versionfile-template.txt", 'r') as t:
            template = string.Template(t.read())
        
        # capture all fields
        data = dict(filevers = f"{self.values['vermajor0']},"\
            f"{self.values['vermajor1']},{self.values['verminor0']}",
            prodvers = f"{self.values['prodmajor0']},"\
            f"{self.values['prodmajor1']},{self.values['prodminor0']}",
            CompanyName = f"{self.values['CompanyName']}",\
            FileDescription = f"{self.values['FileDescription']}",\
            FileVersion = f"{self.values['vermajor0']}."\
            f"{self.values['vermajor1']}.{self.values['verminor0']}",
            InternalName = f"{self.values['InternalName']}",
            LegalCopyright = f"{self.values['LegalCopyright']}",
            OriginalFilename = f"{self.values['OriginalFilename']}",
            ProductName = f"{self.values['ProductName']}",
            ProductVersion = f"{self.values['prodmajor0']}."\
            f"{self.values['prodmajor1']}.{self.values['prodminor0']}",
            )
        new_versionfile = template.substitute(data)
        self.window["_terminal_"].update('')
        self.window["_terminal_"].update(new_versionfile)
        with open(f"{self.values['-workdir-']}/version-file.txt", "w")\
            as output:
            output.write(new_versionfile)
            
    def populate_versionfile(self):
        if os.path.exists(f"{self.values['-workdir-']}/version-file.json"):
            with open(f"{self.values['-workdir-']}/version-file.json", "r") as f:
                loaddatas = json.loads(f.read()) 
        else:
            return
                
        for i, (key, value) in enumerate(loaddatas.items()):
            if key == "filevers":
                self.window['vermajor0'].Update(value.split(',')[0])
                self.window['vermajor1'].Update(value.split(',')[1])
                self.window['verminor0'].Update(value.split(',')[2])
            elif key == "CompanyName":
                self.window['CompanyName'].Update(value)
            elif key == "FileDescription":
                self.window['FileDescription'].Update(value)
            elif key == "InternalName":
                self.window['InternalName'].Update(value)
            elif key == "LegalCopyright":
                self.window['LegalCopyright'].Update(value)
            elif key == "OriginalFilename":
                self.window['OriginalFilename'].Update(value)
            elif key == "ProductName":
                self.window['ProductName'].Update(value)
            elif key == "ProductVersion":
                self.window['prodmajor0'].Update(value.split('.')[0])
                self.window['prodmajor1'].Update(value.split('.')[1])
                self.window['prodminor0'].Update(value.split('.')[2])
    
    def new_versionfile(self):
        with open(f"{appdatadir}/templates/template-workspace-project.json", "r")\
            as f:
            predata = json.loads(f.read()) 

        for i, (key, value) in enumerate(predata.items()):
            if key == "filevers":
                self.window['vermajor0'].Update(value.split(',')[0])
                self.window['vermajor1'].Update(value.split(',')[1])
                self.window['verminor0'].Update(value.split(',')[2])
            elif key == "CompanyName":
                self.window['CompanyName'].Update(value)
            elif key == "FileDescription":
                self.window['FileDescription'].Update(value)
            elif key == "InternalName":
                self.window['InternalName'].Update(value)
            elif key == "LegalCopyright":
                self.window['LegalCopyright'].Update(value)
            elif key == "OriginalFilename":
                self.window['OriginalFilename'].Update(value)
            elif key == "ProductName":
                self.window['ProductName'].Update(value)
            elif key == "ProductVersion":
                self.window['prodmajor0'].Update(value.split('.')[0])
                self.window['prodmajor1'].Update(value.split('.')[1])
                self.window['prodminor0'].Update(value.split('.')[2])
            

if __name__ == '__main__':
    app = ExeMaker()
    pth = startup()
    app.load_workspace(pth)
    app.spec_finder()
    app.start()
