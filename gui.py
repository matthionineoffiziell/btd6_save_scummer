import tkinter as tk
from tkinter import messagebox
import globals
from functions import list_save_names, create_save, delete_save, load_save, export_setings, btd6_exe_valid, btd6_save_dir_valid
from exceptions import SaveNotFoundError
from hotkeys import start_hotkey_listener, stop_hotkey_listener
from hotkey_setter import get_new_hotkey, hotkey_to_string

#puts window infront of every other window
def raise_above_all(window):
    window.attributes("-topmost", True)
    window.attributes("-topmost", False)

class Save():
    def __init__(self, name:str, label:tk.Label, loadButton:tk.Button, deleteButton:tk.Button):
        self.name = name
        self.label = label
        self.loadButton = loadButton
        self.deleteButton = deleteButton

#This class overrides the default error handling functionality of tkinter
class Root(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror('Error', str(val))

class MainWindow(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("BloonsTD6 Save Scummer")
        self.root.geometry("341x312")
        self.pack(fill=tk.BOTH, expand=1)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.column0Width = 30
        self.column1Width = 4
        self.column2Width = 7
        self.inputText = tk.Text(self, height=1, width=self.column0Width)
        self.saveButton = tk.Button(self, text='Save', command=self.create_save_button, width=self.column1Width)
        self.settingsButton = tk.Button(self, text='Settings', command=self.settings_button, width=self.column2Width)
        self.inputText.grid(row=0, column=0)
        self.saveButton.grid(row=0, column=1)
        self.settingsButton.grid(row=0, column=2)
        self.saves = []
        self.init_saves()
        raise_above_all(self.root)
        if globals.BTD6_SAVE_DIR == None or globals.BTD6_EXE == None:
            messagebox.showwarning('Missing Settings', 'BTD6 Save Directory or BTD6 Exe Directory are not set, you need to go to settings and set them to use this program')

    #adds all existing saves
    def init_saves(self):
        saveNames = list_save_names()
        for saveName in saveNames:
            self.add_save(saveName)
        self.place_saves()

    #places or moves saves according to it's position in the saves list
    def place_saves(self):
        for i, save in enumerate(self.saves):
            save.label.grid(row=i + 1, column=0)
            save.loadButton.grid(row=i + 1, column=1)
            save.deleteButton.grid(row=i + 1, column=2)

    #appends save to save list and window
    def add_save(self, saveName:str):
        label = tk.Label(self, text=saveName, width=self.column0Width)
        loadButton = tk.Button(self, text='Load', command=lambda: self.load_save_button(saveName), width=self.column1Width)
        deleteButton = tk.Button(self, text='Delete', command=lambda: self.delete_save_button(saveName), width=self.column2Width)
        self.saves.append(Save(saveName, label, loadButton, deleteButton))
        self.place_saves()

    #removes save from save list and window
    def remove_save(self, saveName:str):
        for i, save in enumerate(self.saves):
            if save.name == saveName:
                save.label.destroy()
                save.loadButton.destroy()
                save.deleteButton.destroy()
                self.saves.pop(i)
                self.place_saves()
                return

    def create_save_button(self):
        saveName = self.inputText.get('1.0', 'end-1c')
        self.inputText.delete('1.0', 'end-1c')
        create_save(saveName)
        self.add_save(saveName)
        add create_save('backup')
        self.add_save('backup')

    def delete_save_button(self, saveName:str):
        answer = messagebox.askyesno('Delete Save Conformation', 'Are you sure you want to delete {0}?'.format(saveName))
        if answer == False:
            return
        self.remove_save(saveName)
        delete_save(saveName)

    def load_save_button(self, saveName:str):
        try:
            load_save(saveName)
        except SaveNotFoundError:
            self.remove_save(saveName)
            raise SaveNotFoundError

    def settings_button(self):
        SettingsWindow(self)

    def save_hotkey(self):
        SaveWindow(self)

    def load_hotkey(self):
        LoadWindow(self)

    def on_close(self):
        stop_hotkey_listener()
        self.root.destroy()

    #called by other threads so exceptions can be raised in a gui
    def raise_excpetion(self, exception):
        messagebox.showerror('Error', str(exception))

class SettingsWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        super().__init__(mainWindow.root)
        self.mainWindow = mainWindow
        self.title('Settings for BloonsTD6 Save Scummer')
        self.geometry('382x156')
        self.make_elements()
        self.place_elements()
        raise_above_all(self)

    def make_elements(self):
        self.exeDirButtonLabel = tk.Label(self, text='BTD6 Exe Directory')
        self.exeDirButtonText = tk.Text(self, height=1, width=30)
        self.exeDirButton = tk.Button(self, text='Set', command=self.set_btd6_exe_button)
        self.saveDirButtonLabel = tk.Label(self, text='BTD6 Save Directory')
        self.saveDirButtonText = tk.Text(self, height=1, width=30)
        self.saveDirButton = tk.Button(self, text='Set', command=self.set_btd6_save_dir_button)
        self.saveHotkeyLabel = tk.Label(self, text='save hotkey')
        self.saveHotkey = tk.Label(self, text=hotkey_to_string(globals.SAVE_HOTKEY))
        self.saveHotkeyButton = tk.Button(self, text='Set', command=self.set_save_hotkey_button)
        self.loadHotkeyLabel = tk.Label(self, text='load hotkey')
        self.loadHotkey = tk.Label(self, text=hotkey_to_string(globals.LOAD_HOTKEY))
        self.loadHotkeyButton = tk.Button(self, text='Set', command=self.set_load_hotkey_button)
        self.quicksaveHotkeyLabel = tk.Label(self, text='quicksave hotkey')
        self.quicksaveHotkey = tk.Label(self, text=hotkey_to_string(globals.QUICKSAVE_HOTKEY))
        self.quicksaveHotkeyButton = tk.Button(self, text='Set', command=self.set_quicksave_hotkey_button)
        self.quickloadHotkeyLabel = tk.Label(self, text='quickload hotkey')
        self.quickloadHotkey = tk.Label(self, text=hotkey_to_string(globals.QUICKLOAD_HOTKEY))
        self.quickloadHotkeyButton = tk.Button(self, text='Set', command=self.set_quickload_hotkey_button)

    def place_elements(self):
        self.exeDirButtonLabel.grid(row=0, column=0)
        self.exeDirButtonText.grid(row=0, column=1)
        self.exeDirButton.grid(row=0, column=2)
        self.saveDirButtonLabel.grid(row=1, column=0)
        self.saveDirButtonText.grid(row=1, column=1)
        self.saveDirButton.grid(row=1, column=2)
        self.saveHotkeyLabel.grid(row=2, column=0)
        self.saveHotkey.grid(row=2, column=1)
        self.saveHotkeyButton.grid(row=2, column=2)
        self.loadHotkeyLabel.grid(row=3, column=0)
        self.loadHotkey.grid(row=3, column=1)
        self.loadHotkeyButton.grid(row=3, column=2)
        self.quicksaveHotkeyLabel.grid(row=4, column=0)
        self.quicksaveHotkey.grid(row=4, column=1)
        self.quicksaveHotkeyButton.grid(row=4, column=2)
        self.quickloadHotkeyLabel.grid(row=5, column=0)
        self.quickloadHotkey.grid(row=5, column=1)
        self.quickloadHotkeyButton.grid(row=5, column=2)

    def set_btd6_exe_button(self):
        textInput = self.exeDirButtonText.get('1.0', 'end-1c')
        self.exeDirButtonText.delete('1.0', 'end-1c')
        if not textInput.endswith('\\'):
            textInput += '\\'
        globals.BTD6_EXE = textInput + 'BloonsTD6.exe'
        if not btd6_exe_valid():
            messagebox.showwarning('Incorrect Btd6 Exe Directory Warning', 'The directory you entered for the btd6 exe directory is incorrect, visit the github for help on finding the directory')
            return
        export_setings()

    def set_btd6_save_dir_button(self):
        textInput = self.saveDirButtonText.get('1.0', 'end-1c')
        self.saveDirButtonText.delete('1.0', 'end-1c')
        if not textInput.endswith('\\'):
            textInput += '\\'
        globals.BTD6_SAVE_DIR = textInput
        if not btd6_save_dir_valid():
            messagebox.showwarning('Incorrect Btd6 Exe Directory Warning', 'The directory you entered for the btd6 save directory is incorrect, visit the github for help on finding the directory')
            return
        export_setings()

    def set_save_hotkey_button(self):
        stop_hotkey_listener()
        globals.SAVE_HOTKEY = get_new_hotkey()
        self.saveHotkey.config(text=hotkey_to_string(globals.SAVE_HOTKEY))
        export_setings()
        start_hotkey_listener(self.mainWindow)

    def set_load_hotkey_button(self):
        stop_hotkey_listener()
        globals.LOAD_HOTKEY = get_new_hotkey()
        self.loadHotkey.config(text=hotkey_to_string(globals.LOAD_HOTKEY))
        export_setings()
        start_hotkey_listener(self.mainWindow)

    def set_quicksave_hotkey_button(self):
        stop_hotkey_listener()
        globals.QUICKSAVE_HOTKEY = get_new_hotkey()
        self.quicksaveHotkey.config(text=hotkey_to_string(globals.QUICKSAVE_HOTKEY))
        export_setings()
        start_hotkey_listener(self.mainWindow)

    def set_quickload_hotkey_button(self):
        stop_hotkey_listener()
        globals.QUICKLOAD_HOTKEY = get_new_hotkey()
        self.quickloadHotkey.config(text=hotkey_to_string(globals.QUICKLOAD_HOTKEY))
        export_setings()
        start_hotkey_listener(self.mainWindow)

class SaveWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        super().__init__(mainWindow.root)
        self.mainWindow = mainWindow
        self.title('Save Window')
        self.inputText = tk.Text(self, height=1, width=30)
        self.saveButton = tk.Button(self, text='Save', command=self.save_button)
        self.inputText.grid(row=0, column=0)
        self.saveButton.grid(row=0, column=1)
        raise_above_all(self)

    def save_button(self):
        saveName = self.inputText.get('1.0', 'end-1c')
        create_save(saveName)
        self.mainWindow.add_save(saveName)
        create_save('backup')
        self.mainWindow.add_save('backup')
        self.destroy()

class LoadWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        super().__init__(mainWindow.root)
        self.mainWindow = mainWindow
        self.title('Load Window')
        self.inputText = tk.Text(self, height=1, width=30)
        self.loadButton = tk.Button(self, text='Load', command=self.load_button)
        self.inputText.grid(row=0, column=0)
        self.loadButton.grid(row=0, column=1)
        raise_above_all(self)
        
    def load_button(self):
        saveName = self.inputText.get('1.0', 'end-1c')
        try:
            load_save(saveName)
        except SaveNotFoundError:
            self.mainWindow.remove_save(saveName)
            raise SaveNotFoundError
        finally:
            self.destroy()
