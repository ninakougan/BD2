# -*- coding: utf-8 -*-
"""
MID.py

Monetary incentive delay task with valences for reward/loss and a neutral
condition, for 6 total trial types.

This is the practice task to be done before going into the MRI scanner.

Based on code originally written by @nivreggev, see README
Modified by Haroon Popal (hspopal on GitHub)
"""

from psychopy import gui, visual, core, data, event, logging, monitors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from numpy.random import random, shuffle
import random
import os
import csv
import pandas as pd
import numpy as np
import time
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning) 

############################################################################
# SET UP
############################################################################

# Setting up some user-defined variables

DEBUG = False  # Used for editing code and testing
expName = "MID"
version = "1.1"
data_dir = "../data/"  # Location of outputs to be generated
stim_dir = "../stimuli/"  # Location of stimuli
inst_dir = stim_dir+"instructions/"  # Location of instructions directory

num_runs = 1

# Trials per run
num_trials = 6

initial_fix_duration = 5  # Added time to make sure homogenicity of magnetic field is reached
closing_duration = 8.0  # Added time at end of last run to make sure we capture enough

# Trial times
cue_time = 2.0  # How long the cue is displayed (in seconds)
fix_after_cue_range = [2.0,2.5]  # Inter-stimulus interval
min_target_dur = 0.1  # Sets the minimum presentation time for target (in seconds)
inital_target_dur = 0.5  # Initial presentation of target (in seconds)
isi_target_isi_time = 4  # Total time between end of cue, and right before feedback
feedback_time = 2.0  # How long the trial + total reward feedback is displayed (in seconds)
fix_ITI = [2, 4, 6] * 16  # Inter-trial interval timings

# Shuffle ITIs
random.shuffle(fix_ITI)

# How much to speed up/down target windows (not necessary for practice)
single_speed_factor = 0.02  

total_earnings = 0


# Define accepted inputs
# These are the buttons that are pressed by the participant and experimentor
forwardKeys = ['1','6']  # Used to advance through the task instructions
backKey = '2'  # "Secret" key to go back in the instructions
startKeys = ['enter','return']  # Used to start task after instructions
ttlKey = "5"
expKeys = ['1','2','6']
escapeKeys = ['escape', 'esc']  # Used to exit out of the task

# Define some variables that are used to rerun the task
rerun_MRT = 'r'
end_MRT_Keys = startKeys + [rerun_MRT]


# Defining some initialization functions

# Create the presentation screen
def make_screen():
    """
    Generates screen variables.
    WIMR scanner screen is set to 800x600 for a different task,
    so keep that resolution since bars on the side do not affect this.
    """

    if fmri:
        win_res = [800, 600]
        screen=1
    else:
        win_res = [1920, 1080]
        screen=0
    exp_mon = monitors.Monitor('exp_mon')
    exp_mon.setSizePix(win_res)

    win = visual.Window(size=win_res, screen=screen, allowGUI=True,
                        fullscr=True, monitor=exp_mon, units='height',
                        color="Black")
    return(win_res, win)

# Define function for saving data
def start_datafiles(_thisDir, expName, expInfo, data_dir, sn, session, fmri):
    """Creates name for datafile (after checking for old one)"""
    pad = 4-len(str(sn))
    snstr = '0'*pad + str(sn)
    fname = expName + '_' + ['practice', 'fmri'][fmri] + '_' + snstr
    if os.path.exists(fname):
        if i == fname + '.csv':
            warndlg = gui.Dlg(title='Warning!')
            warndlg.addText('A data file with this number already exists.')
            warndlg.addField('Overwrite?\t\t', initial="no")
            warndlg.addField('If no, new SN:\t', initial='0')
            warndlg.show()
            if gui.OK:
                over = warndlg.data[0].lower() == 'no'
            else:
                core.quit()
            if over:
                sn = int(warndlg.data[1])
                pad = 4-len(str(sn))
                snstr = '0'*pad + str(sn)
                fname = expName + '_'  + ['practice', 'fmri'][fmri] + '_' + snstr
    filename = _thisDir + os.sep + data_dir + os.sep + snstr + os.sep + fname + '_ses-'+str(session)
    print('\n\n'+filename+'\n\n')
    return(filename)

# Define function for displaying instructions
def display_instructions_file(inst_file, instructions, run):
    # Input a file to be read
    inname = _thisDir + os.sep + inst_dir + os.sep + inst_file
    infile = pd.read_csv(inname)
    
    # Pull out the column that specifies the images for each page of the instructions
    instr_images = list(infile['images'])
    
    endOfInstructions = False
    instructLine = 0
    
    # Loop through instructions
    while not endOfInstructions:
        
        # Print the instructions on the screen
        instructPrompt.setText(instructions[instructLine])
        instructPrompt.draw()
        
        # Present image if relevant
        
        # Create the task order page. This is "hard coded" instead of using
        # an image so that there is consitent resolution on different screens
        if instr_images[instructLine] == 'task_order':
                fix1_exmp = visual.TextStim(win, pos=[-0.65, 0.15], 
                                            text='+', height=fontH*2, 
                                            color=text_color, 
                                            flipHoriz=flipHoriz)
                cuex_exmp = visual.ImageStim(win, pos=[-0.35,0.15], size=0.2,
                                             image=stim_dir+"reward_high.png")
                fix2_exmp = visual.TextStim(win, pos=[-0.15, 0.15], text='+', 
                                            height=fontH*2, color=text_color, 
                                            flipHoriz=flipHoriz)
                targ_exmp = visual.Polygon(win, pos=[0.15,0.15], edges=3, 
                                           radius=0.1, fillColor="white")
                fix3_exmp = visual.TextStim(win, pos=[0.35, 0.15], text='+', 
                                            height=fontH*2, 
                                            color=text_color, 
                                            flipHoriz=flipHoriz)
                fdbk_exmp = visual.TextStim(win, pos=[0.65, 0.15], 
                                            text='Hit!\n+$5.00', 
                                            height=fontH*2, 
                                            color=text_color, 
                                            flipHoriz=flipHoriz)
                
                # Draw bottom row of page
                fix1_desc = visual.TextStim(win, pos=[-0.65, -0.15], 
                                            text='Pay attention', 
                                            height=fontH, wrapWidth=0.15,
                                            color=text_color, 
                                            flipHoriz=flipHoriz,
                                            alignText='center')
                cuex_desc = visual.TextStim(win, pos=[-0.35, -0.15], 
                                            text="Cue: don't respond yet", 
                                            height=fontH, wrapWidth=0.15,
                                            color=text_color, 
                                            flipHoriz=flipHoriz, 
                                            alignText='center')
                fix2_desc = visual.TextStim(win, pos=[-0.15, -0.15], 
                                            text='Pay attention', 
                                            height=fontH, wrapWidth=0.15,
                                            color=text_color, 
                                            flipHoriz=flipHoriz, 
                                            alignText='center')
                targ_desc = visual.TextStim(win, pos=[0.15, -0.15], 
                                            text='Respond when solid triangle is on screen', 
                                            height=fontH, wrapWidth=0.15,
                                            color=text_color, 
                                            flipHoriz=flipHoriz, 
                                            alignText='center')
                fix3_desc = visual.TextStim(win, pos=[0.35, -0.15], 
                                            text='Pay attention', 
                                            height=fontH, wrapWidth=0.15,
                                            color=text_color, 
                                            flipHoriz=flipHoriz, 
                                            alignText='center')
                fdbk_desc = visual.TextStim(win, pos=[0.65, -0.15], 
                                            text='Feedback', height=fontH, 
                                            wrapWidth=0.15, color=text_color, 
                                            flipHoriz=flipHoriz, 
                                            alignText='center')
                
                fix1_exmp.draw()
                cuex_exmp.draw()
                fix2_exmp.draw()
                targ_exmp.draw()
                fix3_exmp.draw()
                fdbk_exmp.draw()
                fix1_desc.draw()
                cuex_desc.draw()
                fix2_desc.draw()
                targ_desc.draw()
                fix3_desc.draw()
                fdbk_desc.draw()
                
        # Create the example cues instructions page
        elif 'example' in instr_images[instructLine]:
            temp_cues = dict(cues)
            if instr_images[instructLine].split('_')[-1] == 'cues':
                temp_instr_images = list(temp_cues.keys())
                # Define the layout of the stimuli
                temp_positions = [[xScr/10*-2,yScr/30], [0,yScr/30], 
                                  [xScr/10*2,yScr/30], [xScr/10*-2,yScr/10*-2], 
                                  [0,yScr/10*-2], [xScr/10*2,yScr/10*-2]]
                temp_size = -0.1
            
            else:
                cue_type = instr_images[instructLine].split('_')[-1]
                temp_instr_images = [x for x in list(temp_cues.keys()) if cue_type in x]
                
                if len(temp_instr_images) == 3:
                    temp_positions = [[xScr/10*-2,0], [0,0], [xScr/10*2,0]]
                    
                elif len(temp_instr_images) == 2:
                    temp_positions = [[xScr/10*-1,0], [xScr/10*1,0]]
                
                temp_size = 0
            
            # Draw out stimuli
            for n in range(len(temp_instr_images)):
                temp_image = temp_cues[temp_instr_images[n]]
                temp_image.pos = temp_positions[n]
                temp_image.size += temp_size
                
                temp_image.draw()
            
        
        elif instr_images[instructLine] != 'none' and run == 0:
            # Create the probe image
            if instr_images[instructLine] == 'probe.png':
                inst_target = visual.Polygon(win, edges=3, radius=0.1, fillColor="white", 
                                        pos=(0,yScr/10))
                inst_target.draw()
            # Display the imported image
            else:
                size = 0.4
                position_y = -yScr/20
                instr_image = visual.ImageStim(win, size=size, 
                                           pos=(0, position_y),
                                           image=inst_dir+instr_images[instructLine])
                instr_image.draw()
        
        instructMove.draw()
        win.flip()
        
        # Navigate through the instruction pages
        instructRep = event.waitKeys(keyList=expKeys)
        if instructRep[0] == backKey:
                instructLine -= 1
        elif instructRep[0] in forwardKeys:
            instructLine += 1
        if instructLine >= len(instructions):
            endOfInstructions = True



# Set up experimentor entry screen

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Initialization
expName = expName + version
expInfo = {
    'participant': '',
    'session': '1',
    'fMRI? (yes or no)': 'no',
    'fMRI trigger on TTL? (yes or no)': 'no',
    'fMRI reverse screen? (yes or no)': 'no',
}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # User pressed cancel
expInfo['date'] = data.getDateStr()  # Add a simple timestamp
expInfo['expName'] = expName
sn = int(expInfo['participant'])
session = int(expInfo['session'])

# Check for various experimental handles
if expInfo['fMRI? (yes or no)'].lower() == 'yes':
    fmri = True
else:
    fmri = False

if expInfo['fMRI trigger on TTL? (yes or no)'].lower() == 'yes':
    triggerOnTTL = True
else:
    triggerOnTTL = False

if expInfo['fMRI reverse screen? (yes or no)'].lower() == 'yes':
    flipHoriz = True
else:
    flipHoriz = False


# Run number set to zero to make sure this is a practice run
run = 0

# Data file name creation; later add .psyexp, .csv, .log, etc
filename = start_datafiles(_thisDir, expName, expInfo, data_dir, sn, session, 
                           fmri)

# An ExperimentHandler isn't essential but helps with data saving
exp = data.ExperimentHandler(name=expName, version=version, 
                             extraInfo=expInfo, runtimeInfo=None,
                             originPath=None, savePickle=True, 
                             saveWideText=True, dataFileName=filename)

# Save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # This outputs to the screen, not a file

# Setup the window and presentation constants
[win_res, win] = make_screen()
yScr = 1.
xScr = float(win_res[0])/win_res[1]
fontH = yScr/25
wrapW = xScr/1.5
text_color = 'white'
# Store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None and expInfo['frameRate'] < 300:
    frame_duration = 1.0 / round(expInfo['frameRate'])
else:
    frame_duration = 1.0 / 60.0  # Could not measure, so guess

# Set random seed - participant and session dependent
random.seed(sn * (session + 1100))

instructMoveText = f"Press the button to continue."


instructMove = visual.TextStim(win, text=instructMoveText, height=fontH, 
                                color=text_color, pos=[0, -yScr/3], 
                                flipHoriz=flipHoriz)


# START component code to be run before the window creation

# Create fixation stimulus
fix = visual.TextStim(win, pos=[0, 0], text='+', height=fontH*2, 
                      color=text_color, flipHoriz=flipHoriz)
clock = core.Clock()


# Pre-instructions
instructPre = visual.TextStim(win, text="Please wait.\n\nThe task instructions will begin soon.",
                                     height=fontH, color=text_color, 
                                     pos=[0, 0], wrapWidth=wrapW, 
                                     flipHoriz=flipHoriz)

# Initialize components for Routine "instructions"
instructPrompt = visual.TextStim(win=win, font='Arial', pos=(0, yScr/10), 
                                 height=fontH, wrapWidth=wrapW, 
                                 color=text_color, flipHoriz=flipHoriz);
if fmri:
    endInstructions = "When you are ready to begin the task, place your finger on the button and notify the experimenter."
else:
    endInstructions = "Get Ready!"

instructFinish = visual.TextStim(win, text=endInstructions,
                                     height=fontH, color=text_color, 
                                     pos=[0, 0], wrapWidth=wrapW, 
                                     flipHoriz=flipHoriz)

# Initialize components for task transitions
wait = visual.TextStim(win, pos=[0, 0], text="The task will begin momentarily. Get ready...", height=fontH, color=text_color, flipHoriz=flipHoriz)
endf = visual.TextStim(win, pos=[0, 0], text="Thank you. This part of the experiment is now complete.",wrapWidth=wrapW, height=fontH, color=text_color, flipHoriz=flipHoriz)


# Initialize components for Routine "cue"
cues = {
    'reward.neut': visual.ImageStim(win, size=0.3, pos=[0,0],
                                    image=stim_dir+"reward_neut.png"),
    'reward.low':  visual.ImageStim(win, size=0.3, pos=[0,0],
                                    image=stim_dir+"reward_low_125.png"),
    'reward.high': visual.ImageStim(win, size=0.3, pos=[0,0],
                                    image=stim_dir+"reward_high.png"),
    'loss.neut':   visual.ImageStim(win, size=0.3, pos=[0,0],
                                    image=stim_dir+"loss_neut.png"),
    'loss.low':    visual.ImageStim(win, size=0.3, pos=[0,0],
                                    image=stim_dir+"loss_low_125.png"),
    'loss.high':   visual.ImageStim(win, size=0.3, pos=[0,0],
                                    image=stim_dir+"loss_high.png")}
CueClock = core.Clock()


# Initialize components for Routine "Target"
TargetClock = core.Clock()
Target = visual.Polygon(win, edges=3, radius=0.2, fillColor="white", 
pos=(0,0))


# Initialize components for Routine "Feedback"
FeedbackClock = core.Clock()
trial_feedback = visual.TextStim(win=win, name='trial_feedback',
                                 text='Trial:', font='Arial', 
                                 pos=(0, 0), height=fontH+yScr/20, 
                                 wrapWidth=None, ori=0, color='White', 
                                 colorSpace='rgb', opacity=1, 
                                 flipHoriz=flipHoriz);
exp_feedback = visual.TextStim(win=win, name='exp_feedback',
                               text='Total:', font='Arial', 
                               pos=(0, -yScr/16), height=fontH+yScr/20, 
                               wrapWidth=None, ori=0, color='White', 
                               colorSpace='rgb', opacity=1, 
                               flipHoriz=flipHoriz);

breakPrompt = visual.TextStim(win, text="Take a break. When you are ready to continue, notify the experimenter.", 
                              height=fontH, color=text_color, pos=(0,0), 
                              flipHoriz=flipHoriz)
breakEnd = visual.TextStim(win, text="Get ready", height=fontH, 
                           color=text_color, pos=(0,0), flipHoriz=flipHoriz)
                           
waitPrompt = visual.TextStim(win, text="Please wait\n\n", 
                              height=fontH, color=text_color, pos=(0,0), 
                              flipHoriz=flipHoriz)


# Create some handy timers
globalClock = core.Clock()  # To track the time since experiment started
runClock = core.Clock()  # To track the time since experiment started
trialClock = core.Clock()  # To track the time since trial started
routineTimer = core.CountdownTimer()  # To track time remaining of each (non-slip) routine

# Create the staircase handlers to adjust for individual threshold
# (stairs defined in units of screen frames; actual minimum presentation
# duration is determined by the min_target_dur parameter, the staircase
# procedure can only add frame rates to that minimum value)
if run == 0:
    stepSizes = [6, 3, 3, 2, 2, 1, 1]
else:
    stepSizes = [2, 2, 1, 1]

def make_stairs(nTrials, startVal=15.0):
    return data.StairHandler(startVal=startVal,
        stepType='lin',
        stepSizes=stepSizes,
        minVal=0, maxVal=30,
        nUp=1,
        nDown=2,  # Will home in on the 66% threshold (nUp=1, nDown=3 homes in on 80%)
        nTrials=nTrials,
        extraInfo=expInfo)

perStim = num_runs * num_trials / 6

stairs = {
    'loss.high':   make_stairs(perStim,     15),
    'loss.low':    make_stairs(perStim,     15),
    'loss.neut':   make_stairs(perStim,     15),
    'reward.high': make_stairs(perStim,     15),
    'reward.low':  make_stairs(perStim,     15),
    'reward.neut': make_stairs(perStim,     15),
    }
staircase_end = {}


# Useful functions

def get_keypress():
    keys = event.getKeys()
    if keys:
        return keys[0]
    else:
        return None

def shutdown():
    print("Logging staircase end values and exiting...")
    stairs = ['loss.high', 'loss.low', 'loss.neut', 
              'reward.high', 'reward.low', 'reward.neut']
    logging.warning(f"Total earnings: {total_earnings}")
    logging.flush()
    win.close()
    core.quit()

def show_stim(stim, duration, pos=[0,0]):
    duration = float(duration)
    t_start = globalClock.getTime()
    routineTimer.reset()
    routineTimer.addTime(duration)
    event.clearEvents(eventType='keyboard')
    rt = None
    while routineTimer.getTime() > 0:
        key = get_keypress()
        if key and key.lower() in escapeKeys:
            logging.warning("Escape pressed, exiting early!")
            shutdown()
        if not rt and key in forwardKeys:
            rt = duration - routineTimer.getTime()
        if stim:
            stim.pos = pos
            stim.draw()
        win.flip()
    return rt
    print('TESTING...'+str(rt)+'\n')

def show_fixation(duration):
    return show_stim(fix, duration, pos=[0,0])



############################################################################
# START EXPERIMENT
############################################################################

# Prep the experiment loop

# Create stimulus presentation list
stim_conds = list(cues.keys())


# Experiment begins

def speed_up(duration):
    return float(duration) * single_speed_factor


# Loop the rest of this for num_runs
while run < num_runs:
    
    # Displaying Instructions
    
    # Keyboard checking is just starting
    event.clearEvents(eventType='keyboard')
    event.Mouse(visible=False)
    
    inst_file = 'practice_instructions.csv'    
    instructions = ["We will now practice the Money Game that you will be doing in the scanner.\n\nYour goal is to win money and avoid losing money.\n\n\n\nThis game has many rounds.\n\nEvery round has the same basic order of events.",
    "First you will see a cross in the middle of the screen, like this:\n\n+\n\nThis means you should focus on the screen and get ready to play. ",
    "Next you will see a cue that tells you if you can win or lose money.\nIt will also tell you how much money you can win or lose for that round.\n\nHere are the 6 possibilities:\n\n\n\n\n\n\n",
    "Then, you will see another cross in the middle of the screen:\n\n\n\n+",
    "Next, a solid WHITE TRIANGLE will appear VERY BRIEFLY on the screen:\n\n \n\n \n\n \n\nTo win money or avoid losing money you need to press the button while the solid WHITE TRIANGLE is on the screen.",
    "For WIN CIRCLES, pressing the button while the solid white triangle is on the screen means you will WIN money.\n\nIf you press too late, you will MISS WINNING money.\n\n\n\n\n\n\n\n",
    "For LOSE SQUARES, pressing the button while the solid white triangle is on the screen means you will NOT LOSE money.\n\nIf you press too late, you WILL LOSE money.\n\n\n\n\n\n\n\n",
    "Make sure to try and respond to every triangle, including for the $0.00 rounds.\n\n\n\n\n\n",
    "We will let you know if you pressed the button in time and if you won or lost money for that round.\n\n\n\n\n\n",
    "During each round, this is the order that you will see things happen:\n\n\n\n\n\n\n\n\n\n",
    "Major points to remember:\n\n1. Do not press the button on the win circles, lose squares, or the crosses. Just respond to the SOLID WHITE TRIANGLES.\n\n2. Try to press the button EVERY time you see the solid white triangle.\n\n3. The SOLID WHITE TRIANGLE appears VERY BRIEFLY, so you will have to press the button QUICKLY when you see it.\n\n4. Things move fast in this game, so you will want to keep your finger on the button, ready to respond.",
    "Any Questions?\n\nPlease ask them now."]
    
    display_instructions_file(inst_file, instructions, run)
    
    
    print("end of instructions, hit enter to continue")
    logging.flush()
    instructFinish.draw()
    win.flip()
    event.waitKeys(keyList=startKeys)
    
    print("instructions complete, continuing")
    logging.flush()
    
    # Reset the non-slip timer for next routine
    routineTimer.reset()
    event.clearEvents(eventType='keyboard')
    
    
    # Determine order of stimuli for run
    if run == 0:  # RT run
        stim_list = stim_conds
        # Trials per run
        num_trials = 6
        
    else:  # Run 1 or 2
        # Trials per run
        num_trials = 48
        # Find the appropriate number of repetitions for each condition
        n_cond_reps = int(num_trials/len(stim_conds))
        
        # Create appropriate number of presentations for each condition type
        stim_list = stim_conds*n_cond_reps
    
    # Set/reset trial number for a new run
    trial_number = 0
    
    # Randomize stimuli order
    random.shuffle(stim_list)

    # Create a dataframe for the event file
    order = pd.DataFrame(np.transpose([list(np.arange(1,len(stim_list)+1)), stim_list]),
                         columns=['trial.num','trial.type'])
    
    # Could delete, but keeping to be similar to the scanner task
    if fmri:
        print(f"waiting for ready, hit {startKeys} after prep scan")
        logging.flush()
        wait.draw()
        win.flip()
        event.waitKeys(keyList=fMRI_trigger)

    # Wait for TR signal if in scanner
    if triggerOnTTL:
        print(f"waiting for TTL key {ttlKey} on TR")
        logging.flush()
        wait.draw()
        win.flip()
        event.waitKeys(keyList=ttlKey)
    
    
    print(f"starting run {run} of {num_runs-1}")
    logging.flush()

    runClock.reset()
    if run == 0:
        globalClock.reset()  # To align actual time with virtual time keeper
    
    
    if DEBUG:
        print(f"actual start {globalClock.getTime()}")
    
    
    # Track hit accuracy
    if run == 0:
        target_durs = pd.DataFrame(columns=stairs.keys())
        target_durs.loc[0] = inital_target_dur
    
    hit_tracker = pd.DataFrame(columns=stairs.keys())
    
    
    # Present initial fixation
    if run == 0:
        print('initial fix duration: '+str(initial_fix_duration))
    show_fixation(initial_fix_duration)
    
    # Loop through the trials
    for trial in range(0, num_trials):
        if DEBUG:
            print(f'trial {trial + 1} of {num_trials}')
        
        # Total trial number along all runs
        trial_number += 1
        trial_details = order.iloc[trial]
        trial_type = trial_details['trial.type']
        trial_response = 0
        
        trial_stairs = stairs[trial_type]

        trial_duration_frames = trial_stairs.next()
        staircase_end[trial_type] = trial_duration_frames
        
        # Add data to the experiment handler
        exp.addData('subid', sn)
        exp.addData('session', session)
        exp.addData('run', run)
        exp.addData('trial.system.time', time.asctime())
        
        trialClock.reset()
        
        exp.addData('trial.number', trial_number)
        exp.addData('trial.type', trial_type)
        
        
        def log_detail(x):
            print(f"{x}: {trial_details[x]}")
        
        # ------Prepare to start Routine "Cue"-------
        cue = cues[trial_type]
        
        # Log cue onset time
        exp.addData('Cue.OnsetTime', runClock.getTime())
        cue_rt = show_stim(cue, cue_time, [0,0])  # Is this needed?
        if cue_rt:
            exp.addData('trial.cue_rt', cue_rt)
        
        # Fixation after cue is a random number between two numbers (e.g. 2-2.5s)
        fix_after_cue = random.uniform(fix_after_cue_range[0], 
                                       fix_after_cue_range[1])
        
        # If RT was too fast
        too_fast_rt = show_fixation(fix_after_cue)
        if too_fast_rt:
            print('too fast rt: ', too_fast_rt)
            trial_response = 2
            exp.addData('trial.too_fast_rt', too_fast_rt)
        
        # Log fixation after cue onset
        exp.addData('Dly.OnsetTime', runClock.getTime())
        
        
        # ------Prepare to start Routine "Target"-------
        t = 0
        TargetClock.reset()  # clock

        # Reset the non-slip timer for next routine
        routineTimer.reset()
        continueRoutine = True
        
        routineTimer.addTime(target_durs.loc[0,trial_type])
        
        # Update component parameters for each repeat
        target_response = event.BuilderKeyResponse()
        rt = None
        
        # Keep track of which components have finished
        TargetComponents = [Target, target_response]
        for thisComponent in TargetComponents:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        
        # -------Start Routine "Target"-------
        # Log target onset time
        exp.addData('Tgt.OnsetTime', runClock.getTime())
        
        while continueRoutine and routineTimer.getTime() > 0:
            # Get current time
            t = TargetClock.getTime()

            # Selection screen updates
            if t >= 0.0 and Target.status == NOT_STARTED:
                # Keep track of start time/frame for later
                Target.tStart = t
                # Display target
                Target.setAutoDraw(True)
                # Open response options
                target_response.tStart = t
                target_response.status = STARTED
                # Keyboard checking is just starting
                win.callOnFlip(target_response.clock.reset)  # t=0 on next screen flip
                event.clearEvents(eventType='keyboard')
                theseKeys = []
            
            if Target.status == STARTED and t <= target_durs.loc[0,trial_type]:
                Target.setAutoDraw(True)
                theseKeys = event.getKeys(keyList=forwardKeys)
                
                if len(theseKeys) > 0:  
                    rt = target_response.clock.getTime()
                    target_response.rt = rt
                    if trial_response == 0:
                        trial_response = 1
            
            # Check if all components have finished
            if not continueRoutine:
                break
            continueRoutine = False
            for thisComponent in TargetComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # At least one component has not yet finished

            # Draw fixation if we're done, so we don't leave a blank screen for any frames
            if not continueRoutine:
                fix.draw()
            win.flip()
            
            
        # -------Ending Routine "Target"-------
        for thisComponent in TargetComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        
        # Add the data to the current staircase so it can be used to calculate the next level
        trial_stairs.addResponse(trial_response)

        # Check responses to add RT
        trial_type_count = hit_tracker[trial_type].count()
        if trial_response == 1:
            exp.addData('trial.rt', target_response.rt)
            exp.addData('trial.target_dur', target_response.rt)
            print(f"response: {target_response.rt}")
            hit_tracker.loc[trial_type_count,trial_type] = 1
        elif trial_response == 2 and rt:
            exp.addData('trial.rt', target_response.rt)
            exp.addData('trial.target_dur', target_response.rt)
            print(f"response: {target_response.rt}")
            hit_tracker.loc[trial_type_count,trial_type] = 0
        else:
            exp.addData('trial.target_dur', target_durs.loc[0,trial_type])
            print(f"response: none during stim")
            hit_tracker.loc[trial_type_count,trial_type] = 0
        logging.flush()
        
        # Calculate trial condition hit rate
        hit_rate = hit_tracker[trial_type].sum() / hit_tracker[trial_type].count()        
        
        if hit_rate >= 0.66:
            target_durs.loc[0,trial_type] -= single_speed_factor  # Subtract 20ms
        else:
            target_durs.loc[0,trial_type] += single_speed_factor  # Add 20ms
        
        print(trial_type + ' duration is: '+str(target_durs.loc[0,trial_type]))
        if target_durs.loc[0,trial_type] < min_target_dur:
            target_durs.loc[0,trial_type] = min_target_dur
        routineTimer.addTime(target_durs.loc[0,trial_type])

        reward = 0

        # Update trial components
        if trial_type == 'reward.high' and trial_response == 1:
            reward = 5.0
        elif trial_type == 'reward.low' and trial_response == 1:
            reward = 1.25
        elif trial_type == 'reward.neut' and trial_response == 1:
            reward = 0.0
        elif trial_type == 'loss.high' and not trial_response == 1:
            reward = -5.0
        elif trial_type == 'loss.low' and not trial_response == 1:
            reward = -1.25
        elif trial_type == 'loss.neut' and not trial_response ==1:
            reward = 0.0

        exp.addData('trial.reward', reward)
        total_earnings += reward
        if DEBUG:
            print(f"{trial_type} result: {trial_response}, reward is {reward} for total {total_earnings}" )

        # Fixation after stim target
        exp.addData('Fix_after_target.OnsetTime', runClock.getTime())
        
        # Set the fixation after target by accounting for the variable target
        # time window
        if rt:
            fix_after_target = isi_target_isi_time - fix_after_cue - rt
        else:
            fix_after_target = isi_target_isi_time - fix_after_cue - target_durs.loc[0,trial_type]
        
        too_slow_rt = show_fixation(fix_after_target)
        if too_slow_rt:
            print('too slow rt: ', too_slow_rt)
            trial_response = 3
            exp.addData('trial.too_slow_rt', too_slow_rt)
        
        
        # ------Prepare to start Routine "Feedback"-------
        t = 0
        FeedbackClock.reset()  # clock
        # Reset the non-slip timer for next routine
        routineTimer.reset()
        continueRoutine = True
        routineTimer.addTime(feedback_time)

        def trial_cash_string(r, trial_response):
            if r > 0:
                return f"Hit!\n+${r:.2f}"
            elif r < 0:
                return f"Miss!\n-${abs(r):.2f}"
            elif trial_response == 1:
                return f"Hit!\n${r:.2f}"
            else:
                return f"Miss!\n${r:.2f}"

        def total_cash_string(r):
            if r < 0:
                return f"Miss!\n${r:.2f}"
            else:
                return f"${r:.2f}"

        trial_feedback.setText(trial_cash_string(reward, trial_response))
        
        exp.addData("Tgt.ACC", trial_response)
        exp.addData('Tgt.ACCfeedback', trial_cash_string(reward, trial_response))
        exp.addData('total_earnings', total_earnings)

        # Keep track of which components have finished
        FeedbackComponents = [trial_feedback, exp_feedback]
        for thisComponent in FeedbackComponents:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        
        # Start routine feedback 
        # Log feedback onset time
        exp.addData('Fb.OnsetTime', runClock.getTime())
        
        while continueRoutine and routineTimer.getTime() > 0:
            # Get current time
            t = FeedbackClock.getTime()

            # Feedback screen updates
            if t >= 0.0 and trial_feedback.status == NOT_STARTED:
                # Keep track of start time/frame for later
                trial_feedback.tStart = t
                trial_feedback.setAutoDraw(True)
            frameRemains = 0.0 + feedback_time - win.monitorFramePeriod * 0.75  # most of one frame period left
            if trial_feedback.status == STARTED and t >= frameRemains:
                trial_feedback.setAutoDraw(False)

            # Check if all components have finished
            if not continueRoutine:
                break
            continueRoutine = False
            for thisComponent in FeedbackComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # At least one component has not yet finished

            # Refresh the screen
            if continueRoutine:  # Don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # End routine feedback
        for thisComponent in FeedbackComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)

        # Fixation after stim target
        # We want this to be altered so that the length
        # of the trial is adjusted by the stim difference from 0.5s...
        
        trial_time = trialClock.getTime()
                
        # Log inter trial interval fixation time
        exp.addData('Fix_ITI.OnsetTime', runClock.getTime())
        
        show_fixation(fix_ITI[trial])

        # Completed trial, add some data to log file
        exp.addData('Fix_ITI.Duration', fix_ITI[trial])
        exp.addData('time.trial', trialClock.getTime())
        exp.addData('time.global', globalClock.getTime())
        exp.addData('Winnings', total_earnings)
        
        # Advance to next trial/line in logFile
        exp.nextEntry()
    
    
    # Start task end routine
    if run == 0:
        # Set target durations for the average across all conditions
        target_durs.loc[0] = target_durs.loc[0].mean()
    
    # Export target durations
    if run == 0:
        target_durs.to_csv(filename+'_target_durs-practice.csv', index=False)
    else:
        target_durs.to_csv(filename+'_target_durs-run'+str(run)+'.csv', index=False)
    
    
    if run == 0:
        # If done with the practice run, show the post-practice stuff
        total_earnings = 0
        breakPrompt.draw()
        win.flip()
        event.waitKeys(keyList=forwardKeys)
        
        waitPrompt.draw()
        win.flip()
        print('\n\nHit "Enter" to continue to run 1 or "r" to redo MRT')
        end_MRT = event.waitKeys(keyList=end_MRT_Keys)
        
        if end_MRT[0] == rerun_MRT:
            run = -1
            
    elif run < num_runs - 1:
        # If we are still going and NOT on the last run, show the break messages
        breakPrompt.draw()
        win.flip()
        event.waitKeys(keyList=forwardKeys)
    else:
        # We are on the last run
        show_stim(None, closing_duration)
    
    run += 1

# Completed experimental phase

# End of task message
endf.draw()
win.flip()
print("end of task reached, hit enter to save results and close")
event.waitKeys(keyList=startKeys)

shutdown()
