# Comparing Learning Outcomes: Text-Based vs NAO Robot AI Tutor

This repository contains the code used for the thesis:

**"Comparing Learning Outcomes from Studying with a Text-Based Chatbot vs a NAO Robot Chatbot"**

---

## Overview

This project implements two tutoring systems:

* A **text-based AI tutor** (`text_chat.py`)
* An **embodied NAO robot tutor** (multi-script system)

Both systems connect to the same Large Language Model (LLM) to generate responses, ensuring that differences in learning outcomes are due to the mode of interaction rather than differences in instructional content.

---

## Requirements

* Python 3.x
* Python 2.7 (required for NAO robot interaction)
* Access to a NAO robot (for robotic condition)
* Internet connection for LLM API access

---

## Running the Systems

### Text-Based Tutoring Condition (Standalone)

The text-based system runs independently and does not require the NAO robot.

#### Steps:

1. Open a terminal or command prompt
2. Run:

```bash
python text_chat.py
```

#### Description:

* This program provides a **text-only interface** for interacting with the AI tutor.
* Users type questions directly into the terminal.
* The program sends these inputs to the LLM.
* The LLM generates a response, which is returned and displayed as text.

This system represents the **text-based tutoring condition** used in the study.

---

### NAO Robot Tutoring Condition

The robotic system requires running **two programs simultaneously** using different Python versions.

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
