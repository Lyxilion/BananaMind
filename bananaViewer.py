import tkinter as tk
from PIL import Image, ImageTk
import os

while True:         # ask for a path
    path = input("Path :")
    if os.path.exists(path):        # check if directory exist
        break
    else:
        print("Wrong path")

tab = []
for file in os.listdir(path):       # load every file in the directory
    print(os.path.join(path, file))
    tab.append(os.path.join(path, file))

root = tk.Tk()
root.title("BananaViewer")
width = 1024
height = 720
pic_width = 922
pic_height = 648
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))
root.resizable(0, 0)


def delete(event=None):
    """
        delete the curent images and switch to the next one
    :param event: not used, the keyboard input pass an argument, the button not, so it as to be pass and handle
    """
    if len(tab) == 1:
        os.remove(tab[0])
        print("Done")
        exit()
    else:
        os.remove(tab[0])
        tab.pop(0)
        root.photo = ImageTk.PhotoImage(Image.open(tab[0]).resize((pic_width, pic_height), Image.ANTIALIAS))
        vlabel.configure(image=root.photo)
        print("deleted")


def change_pic(event=None):
    """
        Switch to the next image
    :param event: not used, the keyboard input pass an argument, the button not, so it as to be pass and handle
    """
    if len(tab) == 1:
        print("Done")
        exit()
    else:
        tab.pop(0)
        print("Test")
        root.photo = ImageTk.PhotoImage(Image.open(tab[0]).resize((pic_width, pic_height), Image.ANTIALIAS))
        vlabel.configure(image=root.photo)
        print("kept")


root.photo = ImageTk.PhotoImage(Image.open(tab[0]).resize((pic_width, pic_height), Image.ANTIALIAS))
vlabel = tk.Label(root, image=root.photo)
vlabel.pack()

root.bind("<Left>", delete)
root.bind("<Right>", change_pic)

b = tk.Button(root, text="Delete\n(Left)", command=delete)
b.pack()
b.place(x=150, y=660, height=50, width=250)


b2 = tk.Button(root, text="Keep\n(Right)", command=change_pic)
b2.pack()
b2.place(x=624, y=660, height=50, width=250)

root.mainloop()
