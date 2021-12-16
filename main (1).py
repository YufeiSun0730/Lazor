import io
import PySimpleGUIQt as sg
import os.path
import pandas as pd
from PIL import Image
import cv2
import numpy as np
from time import time,sleep
from PIL import ImageFile
from os import listdir
from os.path import isfile, join
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True


#mypath='/path/to/folder'
#onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
#images = numpy.empty(len(onlyfiles), dtype=object)
#for n in range(0, len(onlyfiles)):
  #images[n] = cv2.imread( join(mypath,onlyfiles[n]) )




def croppedimages(imagestack):
    idx = 0
    yield imagestack[idx]
    idx += idx

def main():
    file_types = [("TIFF(*.tif)","*.tif")]
    Cellidx = []

    file_list_column = [
        [

            sg.Text("C1 Image Path:", size =(20,1)),
            sg.Input(size=(30,1),enable_events=True, key="-C1FILE-"),
            sg.FileBrowse(file_types=file_types, size=(10,1)),
            sg.Button("Load C1 Image", size=(10,1))

        ],


        [
            sg.Text("C2 Image Path:", size=(20,1)),
            sg.Input(size=(30, 1), enable_events=True, key="-C2FILE-"),
            sg.FileBrowse(file_types=file_types, size=(10,1)),
            sg.Button("Load C2 Image", size=(10,1))

        ],

    ]

    image_viewer_column_C1 = [
        [sg.Text("C1 Image :")],
        [sg.Text(size=(40,1), key="-C1TOUT-")],
        [sg.Image(key="-C1IMAGE-", size=(300,300))],
    ]
    image_viewer_column_C2 = [
        [sg.Text("C2 Image:")],
        [sg.Text(size=(40,1), key="-C2TOUT-")],
        [sg.Image(key="-C2IMAGE-", size=(300,300))],
    ]

    cell_type_classifier = [
        [sg.Text('Select cell index', size=(10,1)), sg.InputText(enable_events=True, key='-CELLIDX-'), sg.Button('Go', key='-GO-')],
        [sg.Button("Next", size=(25,1), key='ShowNextImage')],
        [sg.Button("Result", size=(25, 1), key='-Result-')],
        [sg.Radio('None', 'Radio', True, size=(20,1), key='-CellTypeButton0-')],
        [sg.Radio('Normal Cell', 'Radio', True, size=(20,1), key='-CellTypeButton1-')],
        [sg.Radio('CC', 'Radio', True, size=(20,1), key='-CellTypeButton2-')],
        [sg.Radio('KHC', 'Radio', True, size=(20,1), key='-CellTypeButton3-')],
        [sg.Radio('Folded', 'Radio', True, size=(20,1), key='-CellTypeButton4-')],
        [sg.Radio('Unfocused', 'Radio', True, size=(20,1), key='-CellTypeButton5-')],
    ]

    dialog_box = [
        [sg.Text(size=(40,1), key="-output message-")],
    ]

    # Layout

    layout = [

            [sg.Column(file_list_column)],
            [sg.HSeperator()],
            [sg.Column(image_viewer_column_C1),
             sg.VSeperator(),
             sg.Column(image_viewer_column_C2),
             sg.VSeperator(),
             sg.Column(cell_type_classifier)],

            [sg.Column(dialog_box)],

    ]

    # Window
    window = sg.Window(title='Cell Annotation GUI', layout=layout)

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == 'Load C1 Image': #When a file is chosen
            # foldername = values["-FOLDER-"]
            filename = values["-C1FILE-"]
            if os.path.exists(filename):
                image = Image.open(filename)
                # show small size image
                imszc1 = image.size
                #image_1 = np.array(Image.fromarray(image).resize(imsz[0]/10,imsz[1]/10))
                image_smc1 = image.resize((int(imszc1[0]/20),int(imszc1[1]/20)))
                bio = io.BytesIO()
                image_smc1.save(bio, format="TIFF")
                window["-C1IMAGE-"].update(data=bio.getvalue())
                # run cell detection on the image with multiple cells
                # xycoord = celldetection(image)
                # imagestack = cropimages(image,xycoord) #crop images at xycoord and return as imagestack as variable type "generator"

        if event == 'Load C2 Image':  # When a file is chosen
            filename = values["-C2FILE-"]
            if os.path.exists(filename):
                image = Image.open(filename)
                # show small size image
                imszc2 = image.size
                # image_1 = np.array(Image.fromarray(image).resize(imsz[0]/10,imsz[1]/10))
                image_smc2 = image.resize((int(imszc2[0] / 20), int(imszc2[1] / 20)))
                bio = io.BytesIO()
                image_smc2.save(bio, format="TIFF")
                window["-C2IMAGE-"].update(data=bio.getvalue())

        if event == 'GO':
            Cellidx = values['-CELLIDX-'] + 1
            Cur_loc = location[Cellidx]

            try:
                g = croppedimages()
                crop = g.next()
                bio = io.BytesIO()
                crop.save(bio, format="TIFF")
                window["-C1IMAGE-"].update(data=bio.getvalue())
            except:
                window["-output message-"].update(data="you need to load C1 Image first")

        if event == 'ShowNextImage':
            Cellidx = values['-CELLIDX-'] + 1
            Cur_loc = location[Cellidx]

            try:
                g = croppedimages()
                crop = g.next()
                bio = io.BytesIO()
                crop.save(bio, format="TIFF")
                window["-C1IMAGE-"].update(data=bio.getvalue())
            except:
                window["-output message-"].update(data="you need to load C1 Image first")


        celltypes =[0]*len(location[0])

        if event == '-CellTypeButton0-':
            celltypes[Cellidx]= 0
        if event == '-CellTypeButton1-':
            celltypes[Cellidx]= 1
        if event == '-CellTypeButton2-':
            celltypes[Cellidx]= 2
        if event == '-CellTypeButton3-':
            celltypes[Cellidx]= 3
        if event == '-CellTypeButton4-':
            celltypes[Cellidx]= 4
        if event == '-CellTypeButton5-':
            celltypes[Cellidx]= 5


        if event == '-Result-':
            df_loc = pd.DataFrame(Location)
            df_result = pd.DataFrame(celltypes)
            result = pd.concat([df_result, df_loc], axis=1)
            result.to_csv('Annotation_Result.csv')
            sg.Popup('Results Saved!', keep_on_top=True)


if __name__ == '__main__':
    main()



