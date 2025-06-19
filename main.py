import subprocess

def audit():
    subprocess.run(
        ["python", r"F:\Языки\Python\Partfolio\cheat_sheet2\project\cheat_sheet2\preparation\audit\ui\ui_manager.py"])

def editor():
    subprocess.run(["python", r"F:\Языки\Python\Partfolio\cheat_sheet2\project\cheat_sheet2\preparation\editor\side_panel.py"])

def editor2():
    subprocess.run(
        ["python", r"F:\Языки\Python\Partfolio\cheat_sheet2\project\cheat_sheet2\preparation\editor2\ui\side_panel.py"])
def run():
    editor()
    #editor2()
    #audit()


if __name__ == '__main__':
    run()

