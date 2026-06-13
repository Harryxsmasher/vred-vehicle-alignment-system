# VRED Vehicle Alignment System

A Python-based vehicle alignment automation tool developed for automotive VR review environments using Autodesk VRED and HTC Vive Trackers.

---

# Overview

This project was developed for use inside an automotive VR laboratory containing a physical seating buck with a steering wheel and seat assembly.

The objective was to eliminate the repetitive manual alignment process required whenever a new vehicle model was loaded into Autodesk VRED.

Using HTC Vive Tracker data, the system automatically aligns a virtual vehicle with the physical buck, reducing setup time and improving alignment consistency.

---

# Problem Statement

In traditional VR review workflows:

1. Load vehicle model into VRED
2. Manually translate vehicle
3. Manually rotate vehicle
4. Align steering wheel position
5. Verify seating position
6. Repeat adjustments until alignment is acceptable

This process was repeated for every vehicle review session.

---

# Solution

The system uses an HTC Vive Tracker as a spatial reference.

Workflow:

1. Place tracker at desired reference location
2. Launch script
3. Tracker position and rotation are captured
4. Vehicle transforms are calculated automatically
5. Virtual vehicle aligns with physical buck
6. Fine adjustments can be made through GUI controls
7. Alignment settings can be saved as presets

---

# Key Features

## Real-Time Tracking

- HTC Vive Tracker integration
- Live position updates
- Live rotation updates

## Automatic Vehicle Alignment

- Translation alignment
- Rotation alignment
- Steering reference alignment

## Calibration Controls

Adjust:

- X Offset
- Y Offset
- Z Offset
- Rotation X
- Rotation Y
- Rotation Z

## Preset Management

- Save alignment presets
- Load alignment presets
- Reuse calibration settings

## Live Annotation Feedback

Displays:

- Current tracker position
- Tracking status
- Alignment feedback

---

# Technical Architecture

```text
HTC Vive Tracker
        │
        ▼
Tracker Position
Tracker Rotation
        │
        ▼
Transformation Calculation
        │
        ▼
Offset Compensation
        │
        ▼
Vehicle World Transform
        │
        ▼
Autodesk VRED Scene
```

---

# Technologies

| Technology | Purpose |
|------------|----------|
| Python | Core Development |
| Autodesk VRED | Visualization Environment |
| HTC Vive Tracker | Physical Tracking |
| PySide2 | GUI Development |
| PySide6 | Matrix & Quaternion Operations |
| JSON | Preset Storage |

---

# Engineering Applications

- VR Design Reviews
- Vehicle Packaging Reviews
- Ergonomic Studies
- Driver Position Validation
- Automotive Visualization
- XR Engineering Workflows

---

# Benefits

- Eliminates manual alignment effort
- Faster vehicle setup
- Improved positioning consistency
- Repeatable calibration process
- Better VR review efficiency

---

# Future Improvements

- Multi-tracker support
- AI-assisted calibration
- Voice-controlled alignment
- Automatic vehicle recognition
- Cloud-based preset management
- Alignment analytics dashboard

---

# Author

Praveen Mark

Automation Engineer | XR Developer | Engineering Workflow Automation