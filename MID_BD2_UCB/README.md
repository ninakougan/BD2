# MID for BD2 Protocol
# Last Updated 04/23/25 by Nina Kougan (ninakougan@u.northwestern.edu)

## Basic Info

### Directories
MID_BD2_UCB \
├── code \
├── data \
├── misc \
└── stimuli

- **code**
  - Contains all the scripts for this task
- **data**
  - Contains participant-level data files, including output CSVs, log files, and psydat files
- **misc**
  - Catch all for anything else
- **stimuli**
  - Contains the stimulus files, such as the cue images
  - Contains an "instructions" subdirectory that has stimuli for the instruction parts of the task, along with CSVs that contain the word for word instructions
    - There is a separate instructions CSV for each phase of the task (practice, MRT, and main task)
    - Each of these CSVs has a column for the instructions that are presented on each page of the instruction phase
      - Edits to specific language in the instructions can be done by editing the instructions specified in the python scripts
      - The instructions here are just for a reference (importing the instructions from here causes formatting errors)
    - Next to that column is the image that is used (if necessary) for each page on the instructions screen
      - This is the real reason these CSVs exist
      - Sometimes this references a specific .png file in this instructions sudirectory, or it references a "key" that is used to create the instructions imageswithin PsychoPy itself (through nested if-statements)


## Set Up

### Dependecies
- [PsychoPy](https://www.psychopy.org/download.html)
- Clone/download this repository


## Running
1. Open PsychoPy
2. Open the .py file for the portion of the task you want to run (e.g. mid_BD2.py or mid_practice.py)
3. Hit the green "Run Experiment" (play) button

### Practice Task
This task is run via the mid_practice.py script and is done outside of the scanner. The command window in PsychoPy should prompt the experimentors when to hit the "enter" button to start the task after the instructions, if necessary. 

### Mean Reaction Time (MRT) Task
This is run as run 0 in the mid_BD2.py script. There will again be prompts in the command window for the experimentor to start the actual trials after the instructions. After the MRT run, if the mean reaction time is too slow (greater than 0.350 s), a second MRT run will automatically start. After the second MRT run, the task automatically moves to run 1. The output of this task is the "MID1.1_fmri_9998_ses-1_target_durs-MRT.csv" file. This file will be used in run 1, to start the initial duration windows for each condition. 

### MID Task
This task is run via the mid_BD2.py script, as either run 1 or run 2. Run 1 references the "MID1.1_fmri_9998_ses-1_target_durs-MRT.csv" for the initial target durations for each condition, and run 2 references the "MID1.1_fmri_9998_ses-1_target_durs-run1.csv", which has the last target durations for each condition (not means). The "MID1.1_fmri_9998_ses-1_target_durs-run2.csv" file is automatically created and would be used for a run 3, but that is not relevant for the current version of the task. 

#### Restarting a run
If you stop the task in the middle of a run (for example, if the participant needs to use the restroom), the task is built as if this interruption never happens. If run 1 is stopped, when you run 1 again, it will use the same target duration windows as the previous run 1, with the same trial order. The new data will be outputted in a new .csv and .psydat file with an extra "_1" or "_2" suffix in the file name (e.g. MID1.1_fmri_9997_ses-1_2.csv). This second csv will only include the "new" run 1 data and subsequent run 2 data. The old data will be available in MID1.1_fmri_9997_ses-1.csv. Note, that if this interruption happens in run 2, you will need to pull the run 1 data from the old csv and run 2 data from the new csv. As of now, this will have to be done in some post-task processing. 

## Output
A participant's output is put in a folder under the "data" directory, under the participant numeric ID (e.g. 9999). All the data for the participant, including the practice and MRT runs, are in this subject specific folder. The .csv files are the main outputs from the task. There is one set that is outputted after each run. If the task is run over again without changing the session number, the previous final run through will not be overwritten. But, the task outputs a CSV after each trial as a fail-safe in case the task crashes. This file will be overwritten if a new session is not specified. 

Example files:
- MID1.1_fmri_9999_ses-1_target_durs-MRT.csv
  - Target durations calculated from the MRT task
- MID1.1_fmri_9999_ses-1_target_durs-run1.csv (or run2)
  - Target durations calculated from run 1 or 2
- MID1.1_fmri_9999_ses-1.csv
  - Full task output, this is what you want to do analyses
- MID1.1_fmri_9999_ses-1.log
  - A log file created by PsychoPy
- MID1.1_fmri_9999_ses-1.psydat
  - PsychoPy output file. More info [here](https://www.psychopy.org/general/dataOutputs.html)
  - If the task crashes, the data can be recovered from this file, with instructions in the above link



