"""
- CCM (CutiContourMasking) -

This program provides a GUI for generating contoured videos from segmented 
frames and corresponding mask images. It automates the process of applying 
contour detection to pre-processed video data and assembling the processed 
frames into a new video file.

Key Features:
    - Allows the user to directly select an input video file.
    - Allows the user to directly select an output directory for the contoured video.
    - Expects for each video a corresponding workspace folder (located in 
      C:/Users/User/Cutie/workspace) that contains:
            - Segmented frames in the "visualization/davis" folder.
            - Mask images in the "masks" folder.
    - Applies image processing (using Canny edge detection) on the mask 
      images to extract contours, then overlays these contours onto the 
      original segmented frames.
    - Generates an output video with the contour overlay and saves it in 
      the selected output directory, using a filename prefixed with "Contoured_".
    - Allows users to specify parameters such as FPS for the output video.
    - Displays progress and error messages in the GUI to assist with
      troubleshooting.
"""

import os, glob, cv2, numpy as np, tkinter as tk
from tkinter import messagebox, filedialog, ttk

def ContouredVideoProduction(output_video_name: str, segmented_frames: list, masks: list, fps: int = 30, output_dir: str = None, progress_callback=None):
    """
    Creates a contoured video from segmented frames and corresponding masks, then saves it to disk.

    Args:
        output_video_name (str):
            The base name for the output video file (without extension).

        segmented_frames (list of str):
            A list of file paths for the segmented frame images.

        masks (list of str):
            A list of file paths for the mask images corresponding to each frame.

        fps (int):
            Frames per second for the output video.

        output_dir (str):
            The directory where the output video will be saved. If None, a default 
            directory ("Videos/Contoured Videos") is used.

        progress_callback (callable, optional):
            A function that accepts an integer representing the current processed frame number.
            It is called after processing each frame.

    Returns:
        None
    """
    # Use default output directory if none is provided
    if output_dir is None:
        output_video_dir = os.path.join("Videos", "Contoured Videos")
    else:
        output_video_dir = output_dir

    # Create the output directory if it does not exist
    if not os.path.exists(output_video_dir):
        os.makedirs(output_video_dir)

    # Set the prefix for the output video file name
    output_video_prefix = "Contoured_"
    # Construct the full output video path
    output_video_path = os.path.join(output_video_dir, output_video_prefix + output_video_name + ".mp4")

    # Check if there are segmented frames available
    if len(segmented_frames) == 0:
        print(f"[{output_video_name}] No segmented frames available.")
        return

    # Read the first frame to obtain video dimensions
    frame = cv2.imread(segmented_frames[0])
    if frame is None:
        print(f"[{output_video_name}] Failed to read first frame: {segmented_frames[0]}")
        return
    height, width, _ = frame.shape  # Get height and width from the frame

    # Define the video writer with specified codec, fps, and frame size
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Set thresholds for Canny edge detection
    low_threshold = 1
    high_threshold = 256

    # Process each segmented frame along with its corresponding mask
    for i in range(len(segmented_frames)):
        # Read the original segmented frame image
        original_image = cv2.imread(segmented_frames[i])
        # Read the mask image
        mask = cv2.imread(masks[i])
        # If either image fails to load, print an error and continue to the next frame
        if original_image is None or mask is None:
            print(f"[{output_video_name}] Error reading frame or mask at index {i}.")
            continue

        # Apply Canny edge detection on the mask
        edges = cv2.Canny(mask, low_threshold, high_threshold)
        # Convert the edge image to BGR so it can be overlayed on the original image
        colored_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Overlay white contours onto the original image where edges are detected
        contoured_image = np.where(colored_edges > 0, (255, 255, 255), original_image).astype(np.uint8)
        # Write the processed frame to the output video
        video_writer.write(contoured_image)

        # Update progress if a callback function is provided
        if progress_callback:
            progress_callback(i + 1)

    # Release the video writer and close any OpenCV windows
    video_writer.release()
    cv2.destroyAllWindows()
    print(f"[{output_video_name}] Video saved at: {output_video_path}")

class CCMGUI:
    def __init__(self):
        """
        Initializes the CCMGUI class, setting up the main window and GUI elements.

        Attributes:
            root (tk.Tk):
                The main Tkinter window.

            input_video_path (str):
                The full file path of the selected input video.

            output_video_dir (str):
                The directory selected by the user for saving the output video.

            cutie_path (str):
                Path to the workspace folder containing subfolders for each video.

            fps_entry (tk.Entry):
                Entry widget for setting frames per second.

            log_text (tk.Text):
                Text widget for displaying log messages.
        """
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Contoured Video Production GUI")

        # Initialize file paths for input and output
        self.input_video_path = ""  # Path to the selected input video file
        self.output_video_dir = ""  # Path to the selected output directory

        # Set workspace directory for segmented frames and masks
        self.cutie_path = r"C:\Users\User\Cutie\workspace"  # Workspace directory

        # Create a frame for input video selection
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5)
        tk.Label(input_frame, text="Selected Input Video:").pack(side=tk.LEFT, padx=5)  # Label for input video
        self.input_video_label = tk.Label(input_frame, text="None")  # Displays selected input video
        self.input_video_label.pack(side=tk.LEFT, padx=5)
        tk.Button(input_frame, text="Browse...", command=self.select_input_video).pack(side=tk.LEFT, padx=5)  # Button to browse input video

        # Create a frame for output directory selection
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=5)
        tk.Label(output_frame, text="Selected Output Directory:").pack(side=tk.LEFT, padx=5)  # Label for output directory
        self.output_dir_label = tk.Label(output_frame, text="None")  # Displays selected output directory
        self.output_dir_label.pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="Browse...", command=self.select_output_directory).pack(side=tk.LEFT, padx=5)  # Button to browse output directory

        # Create a frame for FPS input
        fps_frame = tk.Frame(self.root)
        fps_frame.pack(pady=5)
        tk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT, padx=5)  # Label for FPS
        self.fps_entry = tk.Entry(fps_frame, width=5)  # Entry widget for FPS
        self.fps_entry.insert(0, "30")  # Set default FPS to 30
        self.fps_entry.pack(side=tk.LEFT, padx=5)

        # Create a frame for the Process and Close buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Process Video", command=self.process_video).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.root.destroy).pack(side=tk.LEFT, padx=5)

        # Create a progress bar to display processing progress
        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)

        # Text widget to display log messages
        self.log_text = tk.Text(self.root, height=10, width=80)
        self.log_text.pack(padx=10, pady=5)

    def log(self, message: str):
        """
        Logs a message to the GUI text widget.

        Args:
            message (str):
                The message to be logged.

        Returns:
            None
        """
        self.log_text.insert(tk.END, message + "\n")  # Insert the message into the log text area
        self.log_text.see(tk.END)  # Scroll to the end of the log text area
        self.root.update_idletasks()  # Update the GUI

    def select_input_video(self):
        """
        Opens a file dialog for the user to select an input video file.

        Returns:
            None
        """
        # Open file dialog to select a video file (only .mp4 files)
        file_path = filedialog.askopenfilename(title="Select Input Video", filetypes=[("MP4 files", "*.mp4")])
        if file_path:
            self.input_video_path = file_path  # Save the selected file path
            self.input_video_label.config(text=os.path.basename(file_path))  # Display the file's base name
            self.log(f"Input video selected: {file_path}")  # Log the selection

    def select_output_directory(self):
        """
        Opens a directory dialog for the user to select an output directory.

        Returns:
            None
        """
        # Open directory dialog to select an output directory
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_video_dir = directory  # Save the selected directory
            self.output_dir_label.config(text=directory)  # Display the selected directory
            self.log(f"Output directory selected: {directory}")  # Log the selection

    def update_progress(self, value: int):
        """
        Updates the progress bar with the current frame number processed.

        Args:
            value (int):
                The current frame count that has been processed.

        Returns:
            None
        """
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def process_video(self):
        """
        Processes the selected video by reading its segmented frames and masks 
        from the corresponding workspace folder, then calling the ContouredVideoProduction 
        function to generate the contoured video.

        Returns:
            None
        """
        # Ensure an input video has been selected
        if not self.input_video_path:
            messagebox.showwarning("No Input Video", "Please select an input video file.")
            return

        # Ensure an output directory has been selected
        if not self.output_video_dir:
            messagebox.showwarning("No Output Directory", "Please select an output directory.")
            return

        # Extract the base name (without extension) of the input video file
        video_name = os.path.splitext(os.path.basename(self.input_video_path))[0]

        # Construct the expected workspace folder path using the base name
        video_folder_path = os.path.join(self.cutie_path, video_name)
        if not os.path.isdir(video_folder_path):
            self.log(f"[{video_name}] Workspace folder does not exist: {video_folder_path}")
            return

        # Build file patterns for segmented frames and masks in the workspace folder
        segmented_frames_pattern = os.path.join(video_folder_path, "visualization", "davis", "*.jpg")
        masks_pattern = os.path.join(video_folder_path, "masks", "*.png")

        # Get sorted lists of segmented frame file paths and mask file paths
        segmented_frames = sorted(glob.glob(segmented_frames_pattern))
        masks = sorted(glob.glob(masks_pattern))

        # Verify that segmented frames are available
        if not segmented_frames:
            self.log(f"[{video_name}] No segmented frames found in: {video_folder_path}")
            return
        # Verify that masks are available
        if not masks:
            self.log(f"[{video_name}] No masks found in: {video_folder_path}")
            return

        try:
            # Retrieve FPS value from the entry widget
            fps = int(self.fps_entry.get())
        except ValueError:
            fps = 30  # Use default FPS if invalid input is provided
            self.log("FPS value is invalid. Using default FPS = 30.")

        self.log(f"[{video_name}] Processing started...")
        # Configure the progress bar maximum value
        self.progress_bar.config(maximum=len(segmented_frames))
        self.progress_bar['value'] = 0

        # Call the external ContouredVideoProduction function with the selected output directory
        # and pass the update_progress method as a progress callback
        ContouredVideoProduction(video_name, segmented_frames, masks, fps, self.output_video_dir, progress_callback=self.update_progress)
        self.log(f"[{video_name}] Processing completed.")

    def run(self):
        """
        Starts the GUI event loop.

        Returns:
            None
        """
        self.root.mainloop()  # Start the Tkinter main event loop

if __name__ == '__main__':
    app = CCMGUI()  # Create an instance of the CCMGUI class
    app.run()       # Run the GUI application