import requests
import random
import io
import os
import threading
import webbrowser
import mpv
import PySimpleGUI as sg
from PIL import Image

data = {"image":None,"thread":None,"filename":None}
boards = ['3', 'a', 'aco', 'adv', 'an', 'b', 'bant', 'biz', 'c', 'cgl', 'ck', 'cm', 'co', 'd', 'diy', 'e', 'fa', 'fit', 'g', 'gd', 'gif', 'h', 'hc', 'his', 'hm', 'hr', 'i', 'ic', 'int', 'jp', 'k', 'lgbt', 'lit', 'm', 'mlp', 'mu', 'n', 'news', 'o', 'out', 'p', 'po', 'pol', 'pw', 'qa', 'qst', 'r', 'r9k', 's', 's4s', 'sci', 'soc', 'sp', 't', 'tg', 'toy', 'trash', 'trv', 'tv', 'u', 'v', 'vg', 'vip', 'vm', 'vmg', 'vp', 'vr', 'vrpg', 'vst', 'vt', 'w', 'wg', 'wsg', 'wsr', 'x', 'xs', 'y']
#worksafe board list:
#boards = ['3', 'a', 'adv', 'an', 'biz', 'c', 'cgl', 'ck', 'cm', 'co', 'diy', 'fa', 'fit', 'g', 'gd', 'his', 'int', 'jp', 'k', 'lgbt', 'lit', 'm', 'mlp', 'mu', 'n', 'news', 'o', 'out', 'p', 'po', 'pw', 'qa', 'qst', 'sci', 'sp', 'tg', 'toy', 'trv', 'tv', 'v', 'vg', 'vip', 'vm', 'vmg', 'vp', 'vr', 'vrpg', 'vst', 'vt', 'w', 'wsg', 'wsr', 'x', 'xs', 'y']

def webm_handler(file_bytes):
    global player
    with open(".data","wb") as f:
        f.write(file_bytes)
    player = mpv.MPV(wid=window['img_gui'].Widget.winfo_id())
    player.loop_playlist = 'inf'
    player.play(".data")

def image_handler(file_bytes):
    thumb_bytes = io.BytesIO()
    im = Image.open(io.BytesIO(file_bytes))
    im.thumbnail(size=(1024,576))
    im.save(thumb_bytes,"PNG")
    window["img_gui"].update(data=thumb_bytes.getvalue())

def get_random():
    if "player" in globals():
        player.terminate()

    imgs = []
    board = random.choice(boards)
    window["img_gui"].update(filename="standby.png")
    window["saved"].update(visible=False)
    r = requests.get("https://a.4cdn.org/{}/threads.json".format(board)).json()
    random_page = r[random.randrange(0,len(r))]["threads"]
    thread = random_page[random.randrange(0,len(random_page))]["no"]
    r = requests.get("https://a.4cdn.org/{}/thread/{}.json".format(board,thread)).json()
    for post in r["posts"]:
        if "tim" in post:
            imgs.append(str(post["tim"])+post["ext"])
    if len(imgs) < 1:
        get_random()
        return
    filename = random.choice(imgs)
    r = requests.get("https://i.4cdn.org/{}/{}".format(board,filename))
    size = int(r.headers.get("Content-Length"))
    img_bytes = io.BytesIO()
    done = 0
    for chunk in r.iter_content(chunk_size=65536):
        done += len(chunk)
        img_bytes.write(chunk)
        window["prog"].update(int((done/size)*10))
    try:
        data["image"] = img_bytes.getvalue()
        data["thread"] = "https://boards.4channel.org/{}/thread/{}".format(board,thread)
        data["filename"] = filename
        window["thread_gui"].update(data["thread"],text_color="cyan")
        window["folder"].update(disabled=False)
        window["get"].update(disabled=False)
        if filename.endswith((".webm",".gif")):
            webm_handler(data["image"])
        else:
            image_handler(data["image"])
    except:
        get_random()

sg.theme("DarkGrey10")
layout = [
    [sg.Image(size=(1024,576),key="img_gui")],
    [sg.Button("Get Random",key="get",bind_return_key=True),sg.Input(visible=False,enable_events=True,key="save_path"),sg.FolderBrowse("Save",disabled=True,key="folder",initial_folder=os.getcwd()),sg.ProgressBar(max_value=10,size=(5,10),key="prog",bar_color=("green","grey")),sg.Text("Thread:"),sg.Text("unknown",key="thread_gui",size=(35,1),enable_events=True,text_color="white"),sg.Text("Saved!",key="saved",size=(6,1),text_color="lightgreen",visible=False)]
]

window = sg.Window("4chan Random",layout=layout,finalize=True)

window["img_gui"].update(filename="standby.png")

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "get":
        window["get"].update(disabled=True)
        threading.Thread(target=get_random).start()
    elif event == "thread_gui" and len(data["thread"]) > 1:
        webbrowser.open(data["thread"])
    elif event == "save_path" and len(values["save_path"])>1:
        with open(os.path.join(values["save_path"],data["filename"]),"wb") as f:
            f.write(data["image"])
            f.close()
        window["saved"].update(visible=True)