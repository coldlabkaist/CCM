# CCM (CutieContourMasking)
This program provides a GUI for generating contoured videos from segmented 
frames and corresponding mask images. It automates the process of applying 
contour detection to pre-processed video data and assembling the processed 
frames into a new video file.

## Features
- Allows the user to directly select an input video file.
- Allows the user to directly select an output directory for the contoured video.
- Expects for each video a corresponding workspace folder (located in C:/Users/User/Cutie/workspace) that contains:
  - Segmented frames in the "visualization/davis" folder.
  - Mask images in the "masks" folder.
- Applies image processing (using Canny edge detection) on the mask images to extract contours, then overlays these contours onto the original segmented frames.
- Generates an output video with the contour overlay and saves it in the selected output directory, using a filename prefixed with "Contoured_".
- Allows users to specify parameters such as FPS for the output video.
- Displays progress and error messages in the GUI to assist with troubleshooting.

## Release Notes
### 25.02.03
CCM 1.0.0 released

## Requirements
- opencv-python>=4.10.0.84
- numpy>=1.26.4
- scipy>=1.31.1

--

Developed by PSW

Copyright (c) 2025, coldlabkaist
