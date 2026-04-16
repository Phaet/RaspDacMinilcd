import time
from time import sleep
import os
import pickle
from subprocess import Popen, PIPE
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument('-k', dest='key', default='KEY_NONE') 

args = parser.parse_args()
key = args.key

state = []

try:
    state_pickle = open('remote_state.pkl', 'rb')
    state = pickle.load(state_pickle)
    state_pickle.close()
except FileNotFoundError:
    state = [False,float(time.time())]
    print("except")
    print(state)

fav_radios = 'FavRadios'
tmp = 'tmp_playlist'
num_keys = {
    'KEY_0': '1',
    'KEY_1': '2',
    'KEY_2': '3',
    'KEY_3': '4',
    'KEY_4': '5',
    'KEY_5': '6',
    'KEY_6': '7',
    'KEY_7': '8',
    'KEY_8': '9',
    'KEY_9': '10'}  # Mapping keys to entry (slot) numbers in the playlist
store_period = 3.0

def shell_command(cmd) :
    result = Popen(cmd, stdout=PIPE, shell=True)
    output = result.communicate()[0].decode("Utf8")
    output = output[:-1]       # suppression du saut de ligne en fin de chaîne
    return output

def play_failure():
    current_pos = shell_command("/usr/bin/mpc -f %position% current")
    shell_command("/usr/bin/mpc rm " + tmp)
    shell_command("/usr/bin/mpc save " + tmp)
    shell_command("/usr/bin/mpc clear")
    shell_command("/usr/bin/mpc load " + fav_radios)
    shell_command("/usr/bin/mpc play 13")  # proc not successful
    sleep(2)
    shell_command("/usr/bin/mpc clear")
    shell_command("/usr/bin/mpc load " + tmp)
    shell_command("/usr/bin/mpc play " + current_pos)
    return

def select_radio(slot):
    global state
    if state[0] and elapsed < store_period:
        print("store key " + key)
        if shell_command("/usr/bin/mpc current"):
            shell_command("/usr/bin/mpc crop")
            shell_command("/usr/bin/mpc load " + fav_radios)
            shell_command("/usr/bin/mpc del " + str(int(slot) + 1))
            shell_command("/usr/bin/mpc mv 1 " + slot)
            shell_command("/usr/bin/mpc single on")
            shell_command("/usr/bin/mpc play 12")  # proc successful
            sleep(2)
            shell_command("/usr/bin/mpc play " + slot)
            shell_command("/usr/bin/mpc rm " + fav_radios)
            shell_command("/usr/bin/mpc save " + fav_radios)
            print(key + " stored")
        else:
            play_failure()
        state = [False,float(time.time())]
    else:
        # Do not proceed if one radio station stops
        shell_command("/usr/bin/mpc single on")
        # Turn shuffle and consume off if on
        shell_command("/usr/bin/mpc shuffle off")
        shell_command("/usr/bin/mpc consume off")
        # Clear the player's queue
        shell_command("/usr/bin/mpc clear")
        # Load the FavRadios playlist
        shell_command("/usr/bin/mpc load " + fav_radios)
        # Finally play the selected station
        shell_command("/usr/bin/mpc play " + slot)
        print(key + " selected")
    return

elapsed = float(time.time()) - state[1]

print(elapsed)
           
if key == 'KEY_STORE':
    state = [True, float(time.time())]
elif key in num_keys:     # Select a radio station by number
    select_radio(num_keys[key])
else:
    pass
 
try:
    state_pickle = open('remote_state.pkl', 'wb') 
    pickle.dump(state, state_pickle)
    state_pickle.close()
except FileNotFoundError:
    print("state not saved in state_pickle")