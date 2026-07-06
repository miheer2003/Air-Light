# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
AirLight is an AI-powered gesture-controlled smart lighting system that allows users to seamlessly control a Wi-Fi-enabled Halonix (Tuya) Smart RGB Bulb using only hand gestures captured through a standard desktop webcam. It provides a real-time, on-device, responsive lighting experience.

## Goals
1. **Reliable Gesture Recognition**: Accurately detect hand states (Open Palm, Closed Fist, Pinch, Finger Counting, Swiping) in real-time using MediaPipe.
2. **Local Smart Light Control**: Send immediate network commands to Tuya smart bulbs locally using TinyTuya without cloud latency.
3. **Intuitive User Interface**: Provide a modern desktop GUI via CustomTkinter to display the camera feed, recognized gestures, and bulb connection status.

## Non-Goals (Out of Scope for Baseline)
- Voice Control
- Face Recognition Authentication
- Music Reactive Lighting
- Cloud-based Tuya integration (relying strictly on local network control)

## Users
Desktop users who want a hands-free, sci-fi-like experience for controlling ambient lighting while working, gaming, or streaming at their computer.

## Constraints
- **Technical constraints**: Must run smoothly (high FPS) on consumer-grade CPU hardware. Requires webcam and a local network connection to the Tuya smart bulb.
- **Dependency constraints**: Heavy reliance on OpenCV, MediaPipe, and CustomTkinter ecosystem.

## Success Criteria
- [x] Application launches and displays webcam feed in UI.
- [x] Gestures are accurately mapped to power, brightness, and color changes.
- [x] Tuya bulb responds instantly to detected gestures locally.
