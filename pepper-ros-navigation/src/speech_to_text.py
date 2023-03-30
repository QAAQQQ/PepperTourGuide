import speech_recognition as sr
import os, sys
import pyphonetics.phonetics as pypho
import json
import time
import threading
import rospy
from std_msgs.msg import String

#------------------SETUP BEGINS---------------------------------------
#Print hiding class for use with the Google recogniser, which (for reasons known but to God) decides to print a load
#of stuff out for no reason with no way of stopping it.
#Credit to Alexander C on Stackoverflow https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# Define custom word list
custom_words = ['triple-e', 'eesoc', 'fourier', 'oskar']

metaphone = pypho.Metaphone()


#0 = no debugging, 1 = debugging
debug_flag = 1



custom_words_phonetic = []
for custom_word in custom_words:
    custom_words_phonetic.append(metaphone.phonetics(custom_word))

#This is the trigger word, it's easy to change
trigger = "guide"


#------------------SETUP ENDS---------------------------------------

#------------------TRANSCRIPTION BEGINS---------------------------------------
def stt_transcribe(debug_flag, time_limit,noise_adjust):

    speech_clip = ''
    # Initialize recognizer
    r = sr.Recognizer()
   
    with HiddenPrints():
        mic = sr.Microphone(device_index = 2)

    # Using Microphone as source (can also do it from an audio file, might be necessary when integrating, not sure yet)
    with mic as source:
        if(noise_adjust == 1): #It actually needs to be 1, don't @ me
            if(debug_flag):
                print('Noise adjusting')
            r.adjust_for_ambient_noise(source, 1)

        if debug_flag:
            print("Listening")
        # listen to the microphone
        # add time limit with phrase_time_limit=5 argument
        audio = r.listen(source, phrase_time_limit=time_limit)

    #This suppresses the printed stuff for the recognition if the debug flag is on
    try:
        if ~debug_flag:
            with HiddenPrints():
                speech_clip = r.recognize_google(audio, language="en-UK")
        else:
            speech_clip = r.recognize_google(audio, language="en-UK")
    except:
        speech_clip = ''
    # Using Google Speech Recognition, seems to work much better than PocketSphinx
    if debug_flag:
        try:
            speech_clip = speech_clip
            #print("Heard: " + speech_clip)
        except sr.UnknownValueError:
            print("Please repeat that, I didn't understand")
            speech_clip = ''
        except sr.RequestError as e:
            print("Couln't make request, probably an internet error")
            speech_clip = 'NO INTERNET ACCESS'
    if(debug_flag):
        print(speech_clip)
    return speech_clip

#------------------TRANSCRIPTION ENDS---------------------------------------

#------------------CHECK FOR TRIGGER---------------------------------------

def stt_check_for_trigger(speech_clip, debug_flag):
# Check if the trigger word is detected
    if trigger in speech_clip.lower():
        if debug_flag:
            print("TRIGGER DETECTED")
        if debug_flag:
            print("Before phonetic stuff: " + speech_clip)
        return 1
    else:
        return 0  
#------------------CHECK FOR TRIGGER ENDS---------------------------------------

#------------------PHONETIC ANALYSIS BEGINS---------------------------------------

def stt_phonetic_analylsis(speech_clip, custom_words_phonetic, debug_flag):
    #Set up the ol' metaphone to convert to phonetics
    #for reference, that does not mean "big microphone", it's the object that does the phonetic stuff

    # Loop through the transcribed speech and replace similar-sounding words
    #Todo: make this more efficient by not converting each time - update: done
    #Todo: implement phonetic distance instead - update: doesn't discriminate enough
    #Also maybe todo: use IPA instead/ as well - update: no
    #Optimise using syllable count? - update: does the opposite of optimising
    transcribed_speech = speech_clip #Initialise as the same sentence
    for word in speech_clip.split():

        # Convert the word to its phonetic representation
        iii = 0
        phonetic_word = metaphone.phonetics(word)
        for custom_word_phonetic in custom_words_phonetic:
            iii = iii + 1
            if debug_flag:
                print('Word: ' + phonetic_word + ' Custom Word: ' + custom_word_phonetic + ' Is equal: ' + str(phonetic_word == custom_word_phonetic))
            # If the two phonetic representations are the same, replace the word
            if phonetic_word == custom_word_phonetic:
                transcribed_speech = speech_clip.replace(word, custom_words[iii-1])

    if debug_flag:
        print("After phonetic stuff: " + transcribed_speech)

    return transcribed_speech

def talk(str,topic = 'nlp_input'):
    pub = rospy.Publisher(topic, String, queue_size=15)
    # rospy.init_node('talker', anonymous=True)
    rospy.loginfo(str)
    pub.publish(str)
#=========================MAIN==============================================================
debug_flag = 1 #Debug printing off/on
noise_adjust_flag = 1
while True:
    if (noise_adjust_flag > 30):
        noise_adjust_flag = 0
    #Get speech clip from microphone
    speech_clip = stt_transcribe(debug_flag, 5,noise_adjust_flag)
    transcribed_speech = ''
    if True:#stt_check_for_trigger(speech_clip, debug_flag): #Check if trigger word is present
        transcribed_speech = stt_phonetic_analylsis(speech_clip, custom_words_phonetic, debug_flag) #Phonetic analysis
        #(replace similar sounding words with custom ones, e.g. "Tripoli" to "Triple-E")

    #Print (or put into next function, either way, this is the thing you want)
    #print(transcribed_speech)
    #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print(transcribed_speech)
    talk(transcribed_speech)
    #print(sr.Microphone.list_microphone_names())
    #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")


    #print(transcribed_speech_json)

    noise_adjust_flag = noise_adjust_flag + 1

    #with open('data.json', 'w', encoding='utf-8') as f:
        #json.dump(transcribed_speech, f, ensure_ascii=False, indent=4)
    #transcribed_speech_json = json.dumps([transcribed_speech, time.time()])
   

#Test strings:
#Hello guide please can you show me around the triple e department
#Hello guide how are you
