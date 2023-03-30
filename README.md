# PepperTourGuide
This is a gitub repo for the whole HCR course pepper tour guide project. 

## Navigation
Pepper-ros-navigation[ros package]. 

## NLP

* Persona: Defines the specific response behaviour of the "text-davinci-003" model, shaping outputs to sound more like a tour guide in the EEE department, as well as characterising commands which will be passed to gesture and navigation sub-modules.

### Questions: Provide training examples for the model to enhance its response accuracy and fluency in EEE-specific scenarios.

### Keywords: Using the YAML structure to speedly respond to EEE-specific questions and avoid the model from searching for incorrect answers online, e.g., pre-trained information about Professors, department facilities, rooms, etc.

### History: Keep history conversations and invoke them again for each new question input, in order to simplify conversations and be capable to tackle more complicated
tasks.

### GPT3-ChatBot: Generating response from training data and passing to talker.

### Talker: Publish question and response to pepper, including topics leds, target, goal_cancel.

### ListenerLocal: Subscribe response from topic "nlp_input".

### ListenerRemote: Subscribe topic "speak", and make pepper speak with naoqi api.


## Speech to text & Gestures


## Display
display (JavaScript)

## CV
cv

## Responsibility
CV :Sebastian Gillman, Catalin Stretcu, Issa Bqain\
Gestures: Igor Bodnar, Igor Silin\
Navigation:  Anqi Qiu, Yingkai Yang, Yinglong Liang, Pelin Ulusoy, Zhaoyu Wu\
NLP:  Shifan Chu, Yingjie Qin\
Display: Timothy Moores\
Speech to text: Oskar Mason\
Other: Faris AI-Kayssi
