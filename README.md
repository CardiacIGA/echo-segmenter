# Segmentation procedure



## Getting started

This repository provides the template used for segmenting the COMBAT-VT echocardiogam dataset. It relies on three inputs per patient: AP4CH, AP2CH, and PSAX views in .dicom format. These views are stored in the corresponding data folder and are preselected in terms of quality by the user. Next, the user also specifies the frame number at which end-systoly and end-diastoly are obtained per view. This information is stored in the Excel-file. After these pre-processing steps are taken, the user can execute the main.py script to segment each .dicom file. Results are stored as an image and .txt file containing the segmentation coordinates.

## Steps

- [ ] Add .dicom files in the data folder and update the excel-file;
- [ ] Run the main.py code to segment each of the dicom files -> outputs: image and point data;
- [ ] Run the powerpoint.py code to collect all images into a single powerpoint, to be evaluated by an expert.

## Data/ folder structure

Data/
├── VT01/
│   ├── seq1/
|   |   ├── AP4CH.dicom
|   |   ├── AP2CH.dicom
|   |   ├── PSAX.dicom
|   |   ├── images/
|   |   |   └── AP4CH_ED.png, AP2CH_ED.png, PSAX_ED.png, AP4CH_ES.png, AP2CH_ES.png, PSAX_ES.png
│   |   └── points/
|   |       └── AP4CH_ED.txt, AP2CH_ED.txt, PSAX_ED.txt, AP4CH_ES.txt, AP2CH_ES.txt, PSAX_ES.txt 
|   |
│   ├── seq2/
|   |   ├── AP4CH.dicom
|   |   ├── AP2CH.dicom
|   |   ├── PSAX.dicom
|   |   ├── images/
|   |   |   └── AP4CH_ED.png, AP2CH_ED.png, PSAX_ED.png, AP4CH_ES.png, AP2CH_ES.png, PSAX_ES.png
│   |   └── points/
|   |       └── AP4CH_ED.txt, AP2CH_ED.txt, PSAX_ED.txt, AP4CH_ES.txt, AP2CH_ES.txt, PSAX_ES.txt 
│   └── .../
|   
|   
├── VT02/
│   ├── seq1/
|   |   ├── ..
|   |   ├── 
|   └── .../
|
|
├── C01/
│   ├── seq1/
|   |   ├── ..
|   |   ├── 
|   └── .../
|
└── ...


*_ED : End-diastoly
*_ES : End-systoly    

VT : Ventricular Tachycardia patient
C  : Control patient (no VT patient)