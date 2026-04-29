# Comparing Learning Outcomes: Text-Based vs NAO Robot AI Tutor

This repository contains the code used for the thesis:

**"Comparing Learning Outcomes from Studying with a Text-Based Chatbot vs a NAO Robot Chatbot"**

## Overview

This project implements two tutoring systems:

* A **text-based AI tutor**
* An **embodied NAO robot tutor**

Both systems use a Large Language Model (LLM) to generate responses, allowing comparison of interaction modalities while keeping instructional content consistent.

---

## Requirements

* Python 3.x
* Python 2.7 (required for NAO robot interaction)
* Access to a NAO robot (for robotic condition)
* Internet connection for LLM API access

---

## Running the System

### Text-Based Tutoring Condition

1. Open a terminal or command prompt
2. Run the text-based program:

```bash
python push_to_talk_chat.py
```

3. Type questions directly into the interface and receive responses.

---

### NAO Robot Tutoring Condition

⚠️ The robotic system requires running **two programs simultaneously** using different Python versions.

#### Step 1: Start the NAO speech server (Python 2.7)

Open a command prompt and run:

```bash
python2.7 nao_say_server.py
```

This script handles communication with the NAO robot and is responsible for speech output.

---

#### Step 2: Start the interaction program (Python 3)

Open a **second** command prompt and run:

```bash
python push_to_talk_chat.py
```

This script:

* Captures user input (voice or text)
* Sends it to the LLM
* Forwards responses to the NAO robot

---

#### Important Notes

* Both programs must be running **at the same time**.
* They must be run in **separate command prompts**.
* The two scripts communicate with each other to enable real-time interaction with the robot.
* Ensure the NAO robot is properly connected and configured before starting.

---

## Notes

This code was developed for research purposes and may require additional configuration depending on your system setup and environment.

---

## Author

Carly A. Fritz
New Mexico State University
