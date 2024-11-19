import os
from pydicom.filereader import dcmread
from main import load_excel
from PIL import Image
import imageio
import matplotlib.pyplot as plt
import numpy as np
import numpy as np

def rgb2gray(rgb):# applies the formula to convert RBG into brightness
    return np.dot(rgb, [0.2989, 0.5870, 0.1140])

def DCM2GIF_V2(dicomdir, frame_phases, freeze_time=15):
    dcmfiles  = [file.name for file in os.scandir(dicomdir) if os.path.isfile(file)] # File names
    dcmfiles_names = [file.split('.')[0] for file in dcmfiles]
    try:
        os.mkdir(os.path.join(dicomdir,"gifs"))
    except FileExistsError:
        pass    
    fps = 20

    columns = 3
    rows    = len(dcmfiles)
    
    gif_f  = os.path.join(dicomdir,"gifs",f"OverviewDCM.gif")
    writer = imageio.get_writer(gif_f, mode="i", duration=(1e3/fps))    

    size_dcms = {}
    dcms = {}
    for view, dcmfile in zip(dcmfiles_names, dcmfiles):    
        dcm = dcmread(os.path.join(dicomdir,dcmfile))
        size_dcms[view] = len(dcm.pixel_array)
        dcms[view] = dcm.pixel_array

    
    sizemax = 0
    for view, size in size_dcms.items():
        if size > sizemax:
           sizemax = size
           viewmax = view

    images = []
    for k in range(sizemax): 
        fig = plt.figure(figsize=(10, 7))
        for subplt, (view, dcm_pixarray) in enumerate(dcms.items(),1):
            if k > size_dcms[view]-1: # loop gifs which have fewer frames
                kreal = k - size_dcms[view] * ( k // (size_dcms[view]-1) )
            else:
                kreal = k 
            img = dcm_pixarray[kreal,:,:,:]
            img_ES = dcm_pixarray[frame_phases["ES"][view]-1,:,:,:]
            img_ED = dcm_pixarray[frame_phases["ED"][view]-1,:,:,:]
            img_gray = rgb2gray(img) 

            center_id = 2 + 3*(subplt-1)  
            ## Plot the gif
            fig.add_subplot(rows, columns, center_id)
            plt.imshow(img_gray, cmap="gray")#, aspect='auto')
            # Set title correct
            if kreal == frame_phases["ES"][view]:
                plt.title(f"{view} ES (frame {frame_phases['ES'][view]})")
            elif kreal == frame_phases["ED"][view]:
                plt.title(f"{view} ED (frame {frame_phases['ED'][view]})")
            else:
                plt.title(f"{view}")
            plt.axis("off")

            ## Plot the ES and ED frames
            fig.add_subplot(rows, columns, center_id-1)
            plt.imshow(img_ES, cmap="gray")#, aspect='auto')
            plt.title(f"End systole (frame {frame_phases['ES'][view]})")
            plt.axis("off")

            fig.add_subplot(rows, columns, center_id+1)
            plt.imshow(img_ED, cmap="gray")#, aspect='auto')
            plt.title(f"End Diastole (frame {frame_phases['ED'][view]})")
            plt.axis("off")

        # Save as a temporary figure 'tmp.png'
        plt.savefig(os.path.join(dicomdir,"gifs","tmp.png"))#, bbox_inches="tight", pad_inches=0)
        plt.close()
        image = Image.open(os.path.join(dicomdir,"gifs","tmp.png"))
        freeze_frame_ES = [frame_phases["ES"][iview] for iview in dcmfiles_names]
        freeze_frame_ED = [frame_phases["ED"][iview] for iview in dcmfiles_names]
        if kreal in freeze_frame_ED or kreal in freeze_frame_ES:
            for freeze in range(fps):
                print('Freezing')
                #images.append(image) 
                writer.append_data(np.array(image)) 
        else:
            #images.append(image) 
            writer.append_data(np.array(image)) 
    writer.close()
    #imageio.mimsave(gif_f, images)
    if sizemax != 0:
        os.remove(os.path.join(dicomdir,"gifs","tmp.png")) # remove the temporary file again
    return        


def DCM2GIF(dicomdir, frame_phases, freeze_time=15):
    dcmfiles  = [file.name for file in os.scandir(dicomdir) if os.path.isfile(file)] # File names
    dcmfiles_names = [file.split('.')[0] for file in dcmfiles]
    try:
        os.mkdir(os.path.join(dicomdir,"gifs"))
    except FileExistsError:
        pass    
    fps = 20

    for view, dcmfile in zip(dcmfiles_names, dcmfiles):    
        dcm = dcmread(os.path.join(dicomdir,dcmfile))
        gif_f = os.path.join(dicomdir,"gifs",f"{view}.gif")
        writer = imageio.get_writer(gif_f, mode="I", duration=(1e3/fps))    
        # loop over the frames:
        for k, img in enumerate(dcm.pixel_array, 1): # let enumerate start from 1
            #img = dcm.pixel_array[echo.framenr,:,:,:]
            img_gray = rgb2gray(img)    

            
            fig = plt.imshow(img_gray, cmap="gray", aspect='auto')
            plt.axis("off")
            # Set title correct
            if k == frame_phases["ES"][view]:
                fig.axes.set_title(f"End systole (frame {k})")
            elif k == frame_phases["ED"][view]:
                fig.axes.set_title(f"End diastole (frame {k})")
            else:
                fig.axes.set_title(f"{view}")
            fig.axes.get_xaxis().set_visible(False)
            fig.axes.get_yaxis().set_visible(False)
            plt.savefig(os.path.join(dicomdir,"gifs","tmp.png"), bbox_inches="tight", pad_inches=0)
            image = Image.open(os.path.join(dicomdir,"gifs","tmp.png"))    
            
            if k == frame_phases["ES"][view] or k == frame_phases["ED"][view]:
                for freeze in range(fps):
                    print('Freezing')
                    writer.append_data(np.array(image)) 
            else:
                writer.append_data(np.array(image)) 
        writer.close()
    os.remove(os.path.join(dicomdir,"gifs","tmp.png")) # remove the temporary file again

    return


def generate_gifs_all_patients(data_dir):
    folders = [folder.name for folder in os.scandir(data_dir)]
    for folder in folders:
        patient_folder = os.path.join(data_dir,folder)
        generate_gifs_all_sequences(patient_folder, folder)

    return

def generate_gifs_all_sequences(patient_dir, patient):
    sequences = [sequence.name for sequence in os.scandir(patient_dir)]
    for sequence in sequences:
        frames = get_frames(patient, sequence)
        #DCM2GIF(os.path.join(patient_dir,sequence), frames)   
        DCM2GIF_V2(os.path.join(patient_dir,sequence), frames) 
    return

def get_frames(patient, sequence):
    Excel_ES, Excel_ED = load_excel(patient, sequence[3:])
    views_ES = {row["View"]: row[f'seq. {sequence[3:]}'] for index, row in Excel_ES.iterrows()}
    views_ED = {row["View"]: row[f'seq. {sequence[3:]}'] for index, row in Excel_ED.iterrows()}
    return {"ES": views_ES, "ED": views_ED}
    


def visualize_gifs(directDicom):
    #os.system('start out.gif')
    #os.system(os.path.join(directDicom,'gifs','AP2CH.gif'))
    img = Image.open(os.path.join(directDicom,'gifs','AP2CH.gif'))#.convert('RGB')
    img.show()
    # fig = plt.imshow(img, cmap="gray", aspect='auto')
    # plt.axis("off")
    # # Set title correct
    # #fig.axes.set_title(f"{view}")
    # fig.axes.get_xaxis().set_visible(False)
    # fig.axes.get_yaxis().set_visible(False)
    # plt.show()
    return


def save_frames_all_patients(data_dir):
    folders = [folder.name for folder in os.scandir(data_dir)]
    for folder in folders:
        patient_folder = os.path.join(data_dir,folder)
        save_frames_all_sequences(patient_folder, folder)
    return

def save_frames_all_sequences(patient_dir, patient):
    sequences = [sequence.name for sequence in os.scandir(patient_dir)]
    for sequence in sequences:
        frames = get_frames(patient, sequence)
        save_frames(os.path.join(patient_dir,sequence), frames)
    return


def save_frames(dicomdir, frames):
    dcmfiles = [file.name for file in os.scandir(dicomdir) if os.path.isfile(file)]  # File names
    dcmfiles_names = [file.split('.')[0] for file in dcmfiles]

    phase_name = dict(ES="End systole", ED="End diastole")
    size_dcms = {}
    dcms = {}
    for view, dcmfile in zip(dcmfiles_names, dcmfiles):
        dcm = dcmread(os.path.join(dicomdir, dcmfile))
        size_dcms[view] = len(dcm.pixel_array)
        dcms[view] = dcm.pixel_array


    for subplt, (view, dcm_pixarray) in enumerate(dcms.items(), 1):

        for phase, frame in frames.items():
            if len(dcm_pixarray.shape) == 4:
                img = dcm_pixarray[frame[view]-1, :, :, :]
                img_gray = rgb2gray(img)
            else:
                img_gray = dcm_pixarray[frame[view]-1, :, :]

            fig = plt.figure()
            plt.imshow(img_gray, cmap="gray")
            plt.title(f"{view} {phase_name[phase]}")
            plt.savefig(os.path.join(dicomdir, "images", f"segmentation_{view}_{phase}_raw.png"))
            plt.close()
    return

if __name__ == '__main__':
   directC=os.path.realpath(os.path.dirname(__file__)) # Current directory
   directD=os.path.join(directC,"Data") # Data directory
   patient = "VT01"
   sequence= "seq1"
   directDicom=os.path.join(directD,patient,sequence)
   
   #visualize_gifs(directDicom) 
   # Generate gifs for a single patient and sequence
   #frames = get_frames(patient, sequence)
   #DCM2GIF(directDicom, frames)

   # Generate gifs for a single patient and all its sequences
   #generate_gifs_all_sequences(os.path.join(directD, patient), patient)

   # generate gifs for all patients 
   #generate_gifs_all_patients(directD)

   # Save individual frames
   save_frames_all_patients(directD)

    
   