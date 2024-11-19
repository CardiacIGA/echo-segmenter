from pydicom import dcmread
import os
from segmentation import Segmentation, Echo
import numpy as np
import pandas as pd
import warnings
directC=os.path.realpath(os.path.dirname(__file__)) # Current directory
directD=os.path.join(directC,"Data") # Data directory
def get_direct_seq(patient : str):
    return os.path.join(directD,f"{patient}/")
def get_direct(patient : str, seq: int):
    return os.path.join(directD,f"{patient}/seq{seq}/")
views=("AP4CH","AP2CH","PSAX")

def load_excel(patient, sequence):
    excel = pd.read_excel("echo_information.xlsx", sheet_name=None)
    if patient not in excel.keys():
        raise ValueError(f"Specified patient '{patient}' not recognized!")
    excel = excel[patient]
    excel['Phase'] = excel['Phase'].fillna(method='ffill', axis=0)
    excel = excel.set_index('Phase')
    excel_ED = excel[['View',f'seq. {sequence}']].loc['End diastole']
    excel_ES = excel[['View',f'seq. {sequence}']].loc['End systole']
    return excel_ES, excel_ED

def confirm_prompt(question: str) -> bool:
    reply = None
    while reply not in ("y", "n"):
        reply = input(f"{question} (y/n): ").casefold()
    return (reply == "y")

# Check if the specified file has already been segmented, if so raise warning: Option to resegment or not (Y/n)
def check_segmented_before(phase, specView, filename, phase_name, directP, GUI=False):
    load_txt = Segmentation.load_txt
    if type(specView) == str:
        specView = (specView,)
    if phase:
        if os.path.exists(os.path.join(directP,filename)):
            points_loaded = load_txt(os.path.join(directP,filename))
            views_segmented = [v for v in views if v in points_loaded.keys()  ]
            views_not_segmented = [v for v in views if v not in points_loaded.keys()  ]
            questions = []
            question_views = []
            for viewS in views_segmented:
                if viewS not in specView:
                    continue
                if GUI:
                    question_views.append(viewS)
                    questions += [f"The {viewS} view at {phase_name} has already been segmented, do you want to resegment? (Y/n)"]
                else:
                    answer = confirm_prompt(f"The {viewS} view at {phase_name} has already been segmented, do you want to resegment?")
                    if answer:
                        views_not_segmented.append(viewS)
            if GUI:
                return questions, question_views, views_not_segmented
            else:    
                return views_not_segmented
        if GUI:
            return [], [], list(specView)
        else:
            return list(specView)
    if GUI:
        return [], [], []
    else:    
        return []
    

def GUI_get_segment_views(phase, specView, directP, answered=False, answer_input={}):
    EndSystole, EndDiastole = phase

    seg_ES, views_ES, to_be_segmented_ES = check_segmented_before(EndSystole, specView, "Datapoints ES.txt", "ES", directP, GUI=True)# dict containing questions
    seg_ED, views_ED, to_be_segmented_ED = check_segmented_before(EndDiastole, specView, "Datapoints ED.txt", "ED", directP, GUI=True)
    if not answered: # If we do not have an answer, pose the question first
        return seg_ES, seg_ED
    else:
        segment_ES = to_be_segmented_ES + [views_ES[i] for i, answ in enumerate(answer_input["ES"]) if answ]
        segment_ED = to_be_segmented_ED + [views_ED[i] for i, answ in enumerate(answer_input["ED"]) if answ]
        return {"ES": segment_ES, "ED": segment_ED}



def setup_directories(patient,sequence):
    ## Set up the directories/file names___________________________
    directE = get_direct(patient,sequence) # Echo directory
    files  = [file.name for file in os.scandir(directE) if os.path.isfile(file)] # File names
    filesN = [file.split('.')[0] for file in files]
    directI = os.path.join(directE,"images")
    directP = os.path.join(directE,"points")
    if not os.path.exists(directI):
        os.makedirs(directI)
    if not os.path.exists(directP):
        os.makedirs(directP)
    return files, filesN, directE, directI, directP # list of files, 
                                                    # list of file names without extension, 
                                                    # Echo directory (dicom files folder),
                                                    # image directory, 
                                                    # points directory
   
def return_directP(patient, sequence):
    directE = get_direct(patient,sequence) # Echo directory
    return os.path.join(directE,"points")

def check_filename(file_names, GUI=False):
    # Check if there are unknown/unrecognized file names
    for file in file_names:
        if file not in views:
            if GUI:
                return {"Error": f"ERROR: Unknown file name '{file}.dcm', make sure it has one of the following names: AP4CH, AP2CH, PSAX."}
            else:
                raise ValueError(f"Unknown file name '{file}.dcm', make sure it has one of the following names: AP4CH, AP2CH, PSAX.")
    return {}

def check_missing(files, files_names, GUI=False):
    # Check if we are missing any files (Warning if 1 or 2, error if 3)
    missing = []    
    if len(files) != 3:
        for view in views:
            if view not in files_names:
                missing.append(view)
        if len(missing) == 1:
            warning = f"WARNING: The specified folder is missing a view '{missing[0]}'"
        elif len(missing) == 2:
            warning = f"WARNING: The specified folder is missing two views: '{missing[0]}' and  '{missing[1]}'"
        else:
            if GUI:
                return {"Error": "ERROR: The specified folder does not contain any file"}
            else:
                raise ValueError("The specified folder does not contain any file")
        if GUI:
           return {"Warning": warning} 
        else:
            warnings.warn(warning)
    return {}

def check_framenrs(excel, sequence, GUI=False):
    excel_ES, excel_ED = excel
    # Check if the frame numbers correspond with the length of the number of files, else give Error
    rows_with_nan = [(phase, info['View']) for phase, info in excel_ES.iterrows() if np.isnan(info[f'seq. {sequence}']) and info['view'] in specView]
    for phase, view in rows_with_nan:
        error = f"Unspecified frame number for '{view}' at '{phase}', please specify before segmentation"
        if GUI:
            return {"Error": "ERROR: " + error}
        else:
            raise ValueError(error)
    rows_with_nan = [(phase, info['View']) for phase, info in excel_ED.iterrows() if np.isnan(info[f'seq. {sequence}']) and info['view'] in specView]
    for phase, view in rows_with_nan:
        error = f"Unspecified frame number for '{view}' at '{phase}', please specify before segmentation"
        if GUI:
            return {"Error": "ERROR: " + error}
        else:
            raise ValueError(error)    
    return {}

def give_folder_report(directD):
    # Get all sequence folder names:
    patients_VT = [patient.name for patient in os.scandir(directD) if patient.name[0]=='V']
    patients_C  = [patient.name for patient in os.scandir(directD) if patient.name[0]=='C']
    patients = patients_VT + patients_C # We want to list VT patients first, then control patients
    report_total = ""
    
    all_views  = ["AP4CH", "AP2CH", "PSAX"]
    for patient in patients:
        sequences  = [file.name for file in os.scandir(get_direct_seq(patient))] # File names
        seq_result = {}
        for sequence in sequences:
            load_txt = Segmentation.load_txt
            views_segmented = {}
            views_not_segmented = {}
            #TODO add functionality that prints if a dcm file is missing
            for phase in ("ES","ED"):
                points_file = os.path.join(directD, patient, sequence, "points",f"Datapoints {phase}.txt")
                if os.path.exists(points_file):
                    points_loaded = load_txt(points_file)
                    views_segmented[phase] = [v for v in views if v in points_loaded.keys()  ]
                    views_not_segmented[phase] = [v for v in views if v not in points_loaded.keys()  ]
                    if len(views_not_segmented[phase]) == 0:
                        views_not_segmented[phase] = "Done" # Check/Tick mark that everything is segmented
                else:
                    views_not_segmented[phase] = all_views
            seq_result[sequence] = views_not_segmented
        if len(seq_result) != 0:    
            report_total += print_folder_check(patient, seq_result) # Add individual report to total
        report_total += "\n"
    # Gives you an overview of the folders specified and which are segmented, which are not
    #seq_result = {"seq. 1": {"ES": "AP4CH, AP2CH, PSAX", "ED": "PSAX"}, "seq. 10": {"ES": "AP4CH, PSAX", "ED": "PSAX"}}
    return report_total

def print_folder_check(patient, seq_result):
    # seg_result:
    # {'seq. 1' : {'ES': 'Done', 'ED' : 'Done'}, 'seq. 2': {'ES': 'AP4CH, AP2CH', 'ED' : True}, ...  }
    TICK="\u2714"
    CROSS="\u2716"
    partof_cont="├──" 
    partof_final="└──"

    report = f"{patient}\n"
    final = False
    for k, (seq, value) in enumerate(seq_result.items()):
        if len(seq_result) == 1 or k == len(seq_result) - 1:
            report += partof_final
            final = True
        else:
            report += partof_cont


        result  = f"{CROSS} ES: {value['ES']}\n" if value['ES'] != 'Done' else f"{TICK} ES: {TICK}\n"
        result += " "*(6+len(seq))  if final else "|" + " "*(5+len(seq))
        result += f"{CROSS} ED: {value['ED']}\n" if value['ED'] != 'Done' else f"{TICK} ED: {TICK}\n"
        report += f" {seq}: {result}"
    return report

def save_metadata(dicom_dir):
    dcmfiles  = [file.name for file in os.scandir(dicom_dir) if os.path.isfile(file)]
    heartRates=[];views=[]
    metadata_dir = os.path.join(dicom_dir,"metadata")
    try: 
        os.mkdir(metadata_dir) 
    except FileExistsError: 
        pass 

    for dcm in dcmfiles:
        dicom  = dcmread(os.path.join(dicom_dir,dcm))
        heartRates.append(int(dicom.HeartRate))
        views.append(dcm.split('.')[0])
    # Store metadata
    with open(os.path.join(dicom_dir,metadata_dir,"data.txt"), 'w') as f:
        f.write("Heart Rates (extracted from DICOM file)"+"\n")
        for view, heartRate in zip(views, heartRates):
            f.write(f"{view}: {heartRate}\n")
    return

## Read the information of the echos___________________________
def main(patient, sequence, Phase, specView, specBound, excel, Files, segment_views={}, GUI=False):
    EndSystole, EndDiastole = Phase
    excel_ES, excel_ED = excel
    files, filesN, directE, directI, directP = Files
    save_metadata(directE)
    ## Warnings and Errors_________________________________________
    if not GUI:
        check_filename(filesN)
        check_missing(files, filesN)
        check_framenrs(excel, sequence)
        print(specView)
        segment_views = {"ES": check_segmented_before(EndSystole, specView, "Datapoints ES.txt", "ES", directP),  # views to segment
                         "ED": check_segmented_before(EndDiastole, specView, "Datapoints ED.txt", "ED", directP)}
        print(segment_views)



    def segm(phase, files, framenrs, segment_views):
        # make sure input is correctly ordered

        ## Perform actual segmentation_______________________________________
        segment  = Segmentation()
        echos = []
        heartRate=[]



        for ifile, iview, iframenr in zip(files, segment_views, framenrs):

            # Store the DICOM files incl. relevant data into suitable class object "Echo()"
            echo = Echo()
            echo.dicom    = dcmread(os.path.join(directE,ifile))
            echo.filename = ifile
            echo.framenr  = iframenr
            echo.view     = iview
            echo.segment  = True

            # if loaddata2D:
            #     echo.datapoints2D["endocard"] = datapoints_loaded[f"View {echo.view} of endocard"]
            #     echo.datapoints2D["epicard"]  = datapoints_loaded[f"View {echo.view} of epicard"]
            echos += [echo]


        if os.path.exists(os.path.join(directP,f"Datapoints {phase}.txt")):
            loaded_points = segment.load_txt(os.path.join(directP,f"Datapoints {phase}.txt"))
            for iview in loaded_points.keys():
                if iview not in segment_views:
                    echo = Echo()
                    echo.view = iview
                    echo.datapoints2D = loaded_points[iview]
                    echo.segment = False
                    echos += [echo]
        #echoSegment = [echo for echo in echos if echo.segment] 

        if len(segment_views)!=0:
            points  = segment.manual(*echos, returnPoints=True, boundary=specBound, saveFig=True, phase=phase, outputDir=directI) # Segment the DICOM files manually
            segment.save_to_txt(*echos, filename=f"Datapoints {phase}", outputDir=directP) # save results to txt-file

        return

    def order_input(df, segment_views):
        files  = []
        frmnrs = []
        for segView in segment_views:
            print(segView)
            files.append(segView+'.dcm')
            frmnrs.append(df[df['View'] == segView][f'seq. {sequence}'].values[0]-1) # Shift by 1 since frame numbers start at 1 not 0
        return files, frmnrs, segment_views

    if EndSystole and EndDiastole:
        files_ES, framenrs_ES, views_ES = order_input(excel_ES, segment_views["ES"])
        files_ED, framenrs_ED, views_ED = order_input(excel_ED, segment_views["ED"])
        segm('ES', files_ES, framenrs_ES, views_ES)
        segm('ED', files_ED, framenrs_ED, views_ED)
    elif EndDiastole:
        files_ED, framenrs_ED, views_ED = order_input(excel_ED, segment_views["ED"])
        segm('ED', files_ED, framenrs_ED, views_ED)
    elif EndSystole:
        files_ES, framenrs_ES, views_ES = order_input(excel_ES, segment_views["ES"])
        segm('ES', files_ES, framenrs_ES, views_ES)



if __name__ == '__main__':
    ## User input___________________________________________________
    patient  = 'VT04'   # Patient ID
    sequence = 1        # Sequence ID
    EndSystole  = False  # Specify if EndSystole should be segmented
    EndDiastole = True  # Specify if EndDiastole should be segmented
    specView  = "PSAX"#False    # Specify the view ("AP4CH","AP2CH","PSAX") that you want to segment, False lets you segment all in one go
    specBound = 'all'   # Specify the wall/boundary to be segmented ("Endocard","Epicard"), 'all' lets you segment all boundaries
    #checkframe = False # Set True to inspect the specified frame number in the information.excel
    specView = views if not specView else specView

    #seq_result = {"seq. 1": {"ES": "AP4CH, AP2CH, PSAX", "ED": "PSAX"}, "seq. 10": {"ES": "AP4CH, PSAX", "ED": "PSAX"}}
    #give_folder_report(directD)
    #report = print_folder_check(patient, seq_result)
    

    excel = load_excel(patient, sequence)
    Files = setup_directories(patient,sequence)

    # Get some DICOM info
    files, filesN, directE, directI, directP = Files
    dicom = dcmread(os.path.join(directE, files[2]))
    print(files[2])
    print(dicom)
    #main(patient, sequence, (EndSystole, EndDiastole), specView, specBound, excel, Files)
## TODO Print report (what is segmented, what is not)    
# rootdir = 'path/to/dir'
# for rootdir, dirs, files in os.walk(rootdir):
#     for subdir in dirs:
#         print(os.path.join(rootdir, subdir))