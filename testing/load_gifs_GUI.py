import os
directC=os.path.realpath(os.path.dirname(__file__)) # Current directory
gif=os.path.join(directC,"Data","VT01","seq1","gifs","AP2CH.gif")# Data directory

from tkinter import *
import time
root = Tk()

frameCnt = 12
frames = [PhotoImage(file='testing/AP2CH.gif',format = 'gif -index %i' %(i)) for i in range(frameCnt)]

def update(ind):

    frame = frames[ind]
    ind += 1
    if ind == frameCnt:
        ind = 0
    label.configure(image=frame)
    root.after(100, update, ind)
label = Label(root)
label.pack()
root.after(0, update, 0)
root.mainloop()