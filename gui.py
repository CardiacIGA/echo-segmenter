import PySimpleGUI as sg
from operator import itemgetter
from main import load_excel, setup_directories, main, check_filename, check_framenrs, check_missing, GUI_get_segment_views, give_folder_report
import os, PIL
directC=os.path.realpath(os.path.dirname(__file__)) # Current directory
directD=os.path.join(directC,"Data") # Data directory

# Define colors and the order to use them in (https://personal.sron.nl/~pault/)
colormap={"blue"      : '#4477AA',
          "light_blue": '#77AADD',
          "orange"    : '#EE8866',
          "light_yellow": '#EEDD88',
          "pink"      : '#FFAABB',
          "light_cyan": '#99DDFF',
          "mint"      : '#44BB99',
          "pear"      : '#BBCC33',
          "olive"     : '#AAAA00',
          "pale_grey" : '#DDDDDD',
          "black"     : '#000000',
          "white"     : '#FFFFFF'}
EndSystole  = False
EndDiastole = False
views = "AP4CH","AP2CH","PSAX"
AP4CH=False;AP2CH=False;PSAX=False
error_message = "\n \nThe program is terminated, please restart."
segment_views = {}
terminate = False

color_on = colormap["orange"]# Button color when button is on
color_off= colormap["blue"]  # Button color when button is off
text_on  = colormap["black"] # Text color when button is on
text_off = colormap["white"] # Text color when button is off
bcolor   = (text_off, color_off) # Default button color 
sg.set_options(dpi_awareness=True)
font_example = ("Arial", 11,"italic")

# general layout of interface menu
input_menu = [[sg.Text("Specify the input:", background_color=colormap["pale_grey"], text_color=colormap["black"])],
          [sg.Text("Patient    ", background_color=colormap["pale_grey"], text_color=colormap["black"]), 
           sg.InputText(key="-PATIENT-", size=(5,5)),
           sg.Text("(ex: VT01, VT02, C01, ...)", background_color=colormap["pale_grey"], text_color=colormap["black"], font=font_example)],
          [sg.Text("Sequence", background_color=colormap["pale_grey"], text_color=colormap["black"]), 
           sg.InputText(key="-SEQUENCE-", size=(5,5)),
           sg.Text("(ex: 1, 2, 3, ...)", background_color=colormap["pale_grey"], text_color=colormap["black"], font=font_example)],

          [sg.Button("End systole", key="-ES-", button_color=bcolor), 
           sg.Button("End diastole", key="-ED-", button_color=bcolor), 
           sg.Button("Both", key="-BOTH-", button_color=bcolor)],

          [sg.Button("AP4CH", key="-AP4CH-", button_color=bcolor), 
           sg.Button("AP2CH", key="-AP2CH-", button_color=bcolor), 
           sg.Button("PSAX", key="-PSAX-", button_color=bcolor), 
           sg.Button("All", key="-ALL-", button_color=bcolor)],

          [sg.Button("Check folder", button_color=bcolor, key="-CHECKFOLDER-"), 
           sg.Button("Check frame", button_color=bcolor, key="-CHECKFRAME-"), 
           sg.Button("RUN", button_color=bcolor)]]

## TODO: Maybe add buttons: Check result & Redo segmentation?

log_viewer = [
            [sg.Text('Information log', background_color=colormap["pale_grey"], text_color=colormap["black"])],
            [sg.Output(size=(50,10), key='-OUTPUT-',font="courier")],
            [sg.Input(key='-IN-', do_not_clear=False)]
]



# ----- Full layout -----
layout = [
    [sg.Column(input_menu, background_color=colormap["pale_grey"]),
     sg.VSeperator(),
     sg.Column(log_viewer, background_color=colormap["pale_grey"]),]
]

window = sg.Window(title="Echocardiogram segmentation tool (COMBAT-VT)", layout=layout, margins=(10,10),
                   background_color=colormap["pale_grey"], font='Helvetica', finalize=True, icon="icons/combatvt_echo_2.ico") #
window['-IN-'].bind("<Return>", "_Enter")

while True:
    event, values = window.read()    

    # Check button press -> Execute correct function
    if event == "RUN":
        #TODO check input type (str, int, etc.)
        dict_values = itemgetter("-PATIENT-","-SEQUENCE-")(values)
        dict_bool = [len(dv.strip(' '))>=1 for dv in dict_values]
        empty_input = [input_section for input_section, not_empty in zip(("Patient","Sequence"),dict_bool) if not not_empty]
        if len(empty_input) != 0:
            message = "Please provide an input for "
            for k, empty_in in enumerate(empty_input):
                message += f"'{empty_in}'"
                if len(empty_input) != 1 and k < len(empty_input)-2:
                    message += ", "
                elif k == len(empty_input)-2:
                    message += " and "
                else:
                    message += "."
            sg.popup_ok(message, title="No input",button_color=colormap["orange"], 
                        background_color=colormap["pale_grey"], text_color=colormap["black"], keep_on_top=True)

        elif not EndSystole and not EndDiastole:
              sg.popup_ok("Specify the cardiac phase: 'End systole', 'End diastole', or 'Both'.", title="Specify cardiac phase(s)",button_color=colormap["orange"], 
                          background_color=colormap["pale_grey"], text_color=colormap["black"], keep_on_top=True)
        elif not AP4CH and not AP2CH and not PSAX:
              sg.popup_ok("Specify the echo view to be segmented: 'AP4CH', 'AP2CH', 'PSAX', or 'All'.", title="Specify echo view(s)",button_color=colormap["orange"], 
                          background_color=colormap["pale_grey"], text_color=colormap["black"], keep_on_top=True)
              
        else:
          ## Input
          patient   = values["-PATIENT-"]
          sequence  = int(values["-SEQUENCE-"])
          specView  = [sview for mask, sview in zip([AP4CH,AP2CH,PSAX],views) if mask]
          specBound = 'all'
          excel = load_excel(patient, sequence)
          Files = setup_directories(patient,sequence)
          files, filesN, directE, directI, directP = Files

          ## Check program for input errors/warnings
          for type_message, message in check_filename(filesN, GUI=True).items(): # outputs always error or nothing
            window["-OUTPUT-"].update(message + error_message)
            window.refresh()
            break

          for type_message, message in check_missing(files, filesN, GUI=True).items():
            if type_message == "Error":
                window["-OUTPUT-"].update(message + error_message)
                window.refresh()
                break
            else:
                window["-OUTPUT-"].update(message)
                window.refresh()


          for type_message, message in check_framenrs(excel, sequence, GUI=True).items():    
              window["-OUTPUT-"].update(message)
              window.refresh()

          # Get the segmented views, ask questions and process input
          if len(segment_views) == 0:
            seg_ES, seg_ED = GUI_get_segment_views((EndSystole, EndDiastole), specView, directP, answered=False)
            phaseType = ["ES"]*len(seg_ES) + ["ED"]*len(seg_ED)
            answers={"ES" : [], "ED": []} # Stored answer dict
            accepted_yes = ("Yes", "yes", "y", "ye", "Y", "Ye","YES")
            accepted_no  = ("No", "N", "n", "NO")
            total_q_message = "" # This forms the entirity of the questions (also incl. answered questions) 
            for phase_type, question in zip(phaseType, seg_ES + seg_ED):
                total_q_message += question
                window["-OUTPUT-"].update(total_q_message)
                window.refresh()
                Not_answered = True

                while Not_answered:
                    event, values = window.read()
                    if event == "-IN-" + "_Enter":
                      user_answer = values['-IN-']
                      if user_answer in accepted_yes or user_answer in accepted_no:
                        total_q_message += f" {user_answer} \n"
                        answers[phase_type] += [True if user_answer in accepted_yes else False] # Set answer to more general True or False 
                        Not_answered = False
                      else:
                        total_q_message += "\n---Please provide an answer, either 'Yes' or 'No': "
                      window["-OUTPUT-"].update(total_q_message)
                      window.refresh()
                    if not Not_answered:
                      break

                    if event == sg.WIN_CLOSED:
                       terminate = True
                       break
                    
            segment_views = GUI_get_segment_views((EndSystole, EndDiastole), specView, directP, answered=True, answer_input=answers)
            ## TODO add break when window is closed mid segmentation?

            message_execute_program = "\n---The program is being executed---\n"
            total_q_message += message_execute_program
            window["-OUTPUT-"].update(total_q_message)
            window.refresh()
            ## Run the program
            main(patient, sequence, (EndSystole, EndDiastole), specView, specBound, excel, Files, segment_views=segment_views, GUI=True)

            total_q_message += "---The program was succesfully executed, results are saved in designated folders---"
            window["-OUTPUT-"].update(total_q_message)
            window.refresh()


    # Phase button clicks
    if event == '-ES-':
      if EndSystole:
        window['-ES-'].update(button_color = (text_off,color_off))
        EndSystole = False
      else:
        window['-ES-'].update(button_color = (text_on,color_on))
        EndSystole = True

    if event == '-ED-':
      if EndDiastole:
        window['-ED-'].update(button_color = (text_off,color_off))
        EndDiastole = False
      else:
        window['-ED-'].update(button_color = (text_on,color_on))
        EndDiastole = True

    if event == '-BOTH-':
      if EndSystole and EndDiastole:
        window['-ES-'].update(button_color = (text_off,color_off))
        window['-ED-'].update(button_color = (text_off,color_off))
        EndSystole  = False
        EndDiastole = False         
      else:   
        window['-ES-'].update(button_color = (text_on,color_on))
        window['-ED-'].update(button_color = (text_on,color_on))
        EndSystole = True
        EndDiastole = True


    # View button clicks
    if event == '-AP4CH-':
      if AP4CH:
        window['-AP4CH-'].update(button_color = (text_off,color_off))
        AP4CH = False
      else:
        window['-AP4CH-'].update(button_color = (text_on,color_on))
        AP4CH = True

    if event == '-AP2CH-':
      if AP2CH:
        window['-AP2CH-'].update(button_color = (text_off,color_off))
        AP2CH = False
      else:
        window['-AP2CH-'].update(button_color = (text_on,color_on))
        AP2CH = True

    if event == '-PSAX-':
      if PSAX:
        window['-PSAX-'].update(button_color = (text_off,color_off))
        PSAX = False
      else:
        window['-PSAX-'].update(button_color = (text_on,color_on))
        PSAX = True

    if event == '-ALL-':
      if AP4CH and AP2CH and PSAX:
        window['-AP4CH-'].update(button_color = (text_off,color_off))
        window['-AP2CH-'].update(button_color = (text_off,color_off))
        window['-PSAX-'].update(button_color = (text_off,color_off))
        AP4CH = False
        AP2CH = False 
        PSAX = False        
      else:   
        window['-AP4CH-'].update(button_color = (text_on,color_on))
        window['-AP2CH-'].update(button_color = (text_on,color_on))
        window['-PSAX-'].update(button_color = (text_on,color_on))
        AP4CH = True
        AP2CH = True 
        PSAX = True  



    if event =="-CHECKFOLDER-":
       report = give_folder_report(directD)
       window["-OUTPUT-"].update(report)
       window.refresh()
       
    if event =="-CHECKFRAME-":
       ## Input
       patient   = values["-PATIENT-"]
       sequence  = int(values["-SEQUENCE-"])
       Files = setup_directories(patient,sequence)
       files, filesN, directE, directI, directP = Files

      #  #img = PIL.Image.open(os.path.join(directE,'gifs','AP2CH.gif')).convert('RGB')
      #  for i in range(100000): #os.path.join(directE,'gifs','AP2CH.gif')
      #      if not sg.popup_animated(os.path.join(directE,'gifs','OverviewDCM.gif'), message='Gif plot', time_between_frames=50, no_titlebar=False, background_color='black'): #no_titlebar=False, time_between_frames=100, text_color='black', background_color='white'):
      #         break
      #  sg.popup_animated(None)      # close all Animated Popups
       window["-OUTPUT-"].update("Not implemented yet...")
       window.refresh()

    if event == sg.WIN_CLOSED or terminate:
        break

window.close()


# def image_viewer():
#     file_list_column = [sg.Text("image Folder"), sg.In(size=(25,))]
#     return