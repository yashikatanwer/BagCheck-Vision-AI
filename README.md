# BagCheck-Vision-AI 🎒

## Computer Vision–Powered Pre-Departure Readiness System

BagCheck AI is a real-time computer vision application designed to verify the presence of required personal items before departure.

The system combines a custom-trained YOLO object detection model with context-aware checklists to translate visual observations into actionable **Found / Missing** readiness results.

Rather than simply identifying objects in a camera feed, BagCheck AI evaluates those detections against the user's current requirements — whether preparing for college, a day outing, a gym session, travel, or a custom routine.

---

## Overview

Forgetting a single essential item can disrupt an otherwise planned outing.

BagCheck AI addresses this problem through a simple workflow:

**Select what you need → Scan your belongings → Verify readiness**

The computer vision layer identifies supported objects in real time, while the checklist layer determines whether those objects satisfy the requirements of the selected scenario.

This separation allows the system to distinguish between:

- **What is visible**
- **What is required**
- **What is still missing**

---

## Core Capabilities

- Real-time webcam-based object detection
- Custom-trained YOLO detection model
- Context-aware checklist verification
- 16 supported checklist items
- 14 computer-vision detection classes
- Manual confirmation workflow for non-visual checklist items
- College, Day Outing, Gym and Travel presets
- Fully customizable checklists
- Persistent detection confirmation during an active scan
- Visual bounding-box detection
- Confidence-based object filtering
- Real-time Found / Missing status
- Lightweight Flask web application

---

## How the System Works

### 01 — Define Requirements

The user selects a predefined scenario or creates a custom checklist containing the items required for the activity.

### 02 — Visual Acquisition

The application accesses the device camera and continuously processes the live video stream.

### 03 — Object Detection

The custom YOLO model analyzes incoming frames and identifies supported belongings.

### 04 — Detection Confirmation

Detected objects are filtered using class-specific confidence thresholds and temporal confirmation across multiple frames to reduce transient false detections.

### 05 — Checklist Matching

Confirmed detections are matched against the active checklist.

### 06 — Readiness Assessment

The application presents the resulting state as:

**FOUND** — requirement visually confirmed  
**MISSING** — requirement not yet confirmed

Items such as **ID Card** and **Travel Documents**, which are not part of the computer-vision model, can be manually confirmed by the user.

---

## Supported Checklist Items

BagCheck AI currently supports **16 checklist items**.

### Computer Vision Classes

| Category | Supported Items |
|---|---|
| Essentials | Phone, Wallet, Keys |
| Electronics | Charger, Earbuds |
| Stationery | Notebook, Pen |
| Personal Care | Lip Gloss, Sanitizer |
| Food & Hydration | Water Bottle, Tiffin |
| Accessories | Sunglasses |
| Other | Towel, Tissue Paper |

### Manual Confirmation

- ID Card
- Travel Documents

These two items are intentionally handled through manual confirmation rather than the object detection model.

---

## Intelligent Presets

### College
Designed around everyday academic essentials such as a phone, wallet, ID card, notebook, stationery, hydration and personal-care items.

### Day Outing
Focused on compact everyday essentials including phone, earbuds, wallet, sunglasses, lip gloss, sanitizer and tissues.

### Gym
Focused on workout essentials including phone, water bottle, earbuds, towel and sanitizer.

### Travel
Combines essential personal items with travel-specific requirements such as keys, charger and travel documents.

### Custom
Users can define their own checklist based on their specific requirements.

---

## Computer Vision Model

BagCheck AI uses a custom-trained **YOLO object detection model** built specifically for the application's target object classes.

The model was trained to recognize:

- Phone
- Water Bottle
- Charger
- Earbuds
- Keys
- Lip Gloss
- Notebook
- Pen
- Sanitizer
- Sunglasses
- Wallet
- Tiffin
- Tissue Paper
- Towel
- ID Card
- Travel documents

The application layer maps model predictions to the corresponding checklist requirements.

---

## Dataset

The model was trained using a custom dataset containing **275 labeled images across 16 object classes**.

The dataset was divided into training and validation subsets before model training.

The relatively focused dataset allows the prototype to target a defined set of everyday objects rather than attempting to function as a universal object-recognition system.

---

## Model Evaluation

Performance varies across individual classes due to differences in object appearance, scale, visual similarity and available training examples.

The current implementation is therefore positioned as a **functional computer-vision prototype**, with model accuracy remaining an area for future improvement.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Application | Python |
| Web Framework | Flask |
| Computer Vision | YOLO / Ultralytics |
| Image Processing | OpenCV |
| Frontend | HTML, CSS, JavaScript |
| Model Training | Custom YOLO Dataset |

---

## **Architecture**

```text
                  ┌──────────────────────┐
                  │   Checklist Setup    │
                  │ Preset / Custom      │
                  └──────────┬───────────┘
                             │
                             ▼
┌────────────────┐   ┌──────────────────────┐
│  Device Camera │──▶│  YOLO Object         │
│                │   │  Detection Model     │
└────────────────┘   └──────────┬───────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Detection Filtering │
                     │ & Confirmation      │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Checklist Matching  │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Readiness Assessment│
                     │                     │
                     │ ✓ Found / ✕ Missing │
                     └─────────────────────┘

