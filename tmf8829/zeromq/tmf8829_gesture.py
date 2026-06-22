# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
Simple gesture processing functions
"""

import numpy as np
import time

class DToFGestureRecognizer:
    def __init__(self, min_dist=3.0, max_dist=20.0, buffer_size=4, min_pixels=4):
        """
        Args:
            min_dist (float): Minimum detection range in cm.
            max_dist (float): Maximum detection range in cm.
            buffer_size (int): Number of frames to look back (4 frames @ 5fps = 800ms).
            min_pixels (int): Minimum valid pixels required to consider a hand "present".
        """
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.buffer_size = buffer_size
        self.min_pixels = min_pixels
        
        # History buffers
        self.x_com_history = []
        self.y_com_history = []
        self.z_history = []
        self.cooldown_counter = 0

    def process_frame(self, frame):
        """
        Processes a single 8x8 frame.
        
        Args:
            frame (numpy.ndarray): 8x8 matrix representing distance in cm.
        Returns:
            str: Detected gesture name, or None if no gesture is detected.
        """
        # Handle active cooldowns to prevent double-triggering
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return None

        # 1. Filter data within the range
        mask = (frame >= self.min_dist) & (frame <= self.max_dist)
        valid_pixel_count = np.sum(mask)

        # If the hand leaves the field of view, clear history
        if valid_pixel_count < self.min_pixels:
            self.x_com_history.clear()
            self.y_com_history.clear()
            self.z_history.clear()
            return None

        # 2. Extract Features
        # X Center of Mass (0.0 = Far Left, 7.0 = Far Right)
        col_counts = np.sum(mask, axis=0)
        x_com = np.sum(col_counts * np.arange(8)) / valid_pixel_count

        # Y Center of Mass (0.0 = Top, 7.0 = Bottom)
        row_counts = np.sum(mask, axis=1)
        y_com = np.sum(row_counts * np.arange(8)) / valid_pixel_count

        # Average Depth of the hand
        avg_dist = np.mean(frame[mask])

        # Update history buffers
        self.x_com_history.append(x_com)
        self.y_com_history.append(y_com)
        self.z_history.append(avg_dist)

        if len(self.x_com_history) > self.buffer_size:
            self.x_com_history.pop(0)
            self.y_com_history.pop(0)
            self.z_history.pop(0)

        # 3. Classify Gesture (only when buffer is full)
        if len(self.x_com_history) == self.buffer_size:
            gesture = self._classify()
            if gesture:
                self._clear_buffers()
                self.cooldown_counter = 3  # Cooldown for 3 frames (~600ms)
                return gesture

        return None

    def _classify(self):
        # Calculate total delta across the buffer window (current minus oldest)
        dx = self.x_com_history[-1] - self.x_com_history[0]
        dy = self.y_com_history[-1] - self.y_com_history[0]
        dz = self.z_history[-1] - self.z_history[0]

        # Tuning Thresholds
        X_THRESHOLD = 1.5  # Columns shifted (out of 8)
        Y_THRESHOLD = 1.5  # Rows shifted (out of 8)
        Z_THRESHOLD = 2.5  # Centimeters changed (out of 10)

        # Determine dominant movement axis
        if abs(dx) > X_THRESHOLD and abs(dx) > abs(dy) and abs(dx) > abs(dz):
            if dx < 0:
                return "Swipe left"
            else:
                return "Swipe right"

        if abs(dy) > Y_THRESHOLD and abs(dy) > abs(dx) and abs(dy) > abs(dz):
            if dy < 0:
                return "Swipe up"
            else:
                return "Swipe down"

        if abs(dz) > Z_THRESHOLD and abs(dz) > abs(dx) and abs(dz) > abs(dy):
            if dz < 0:
                return "Palm move near"
            else:
                return "Palm move far"

        return None

    def _clear_buffers(self):
        self.x_com_history.clear()
        self.y_com_history.clear()
        self.z_history.clear()

    
    def process_tmf8829_frame(self, pixelResults):
        """
        Processes a single 8x8 frame from TMF8829.
        
        Args:
            frame: tmf8829 8x8 pixel resuls frame
        Returns:
            print detection if not None
            str: Detected gesture name, or None if no gesture is detected.
        """

        # convert to numpy array, pick only z-distance (not physical distance), pick first peak [0] and convert to cm
        # print(pixelResults)
        frame = np.array([[pixelResults[r][c]['peaks'][0]['z'] for c in range(8)] for r in range(8)])/10
        # snr_array = np.array([[pixelResults[r][c]['peaks'][0]['snr'] for c in range(8)] for r in range(8)])
        # eliminate low confidence values
        # threshold = 0.05 * np.max(snr_array)
        # frame[snr_array < threshold] = 0
        result = self.process_frame(frame)
        if result:
            print(result)


# ==========================================
# Example Usage Simulation
# ==========================================
if __name__ == "__main__":
    recognizer = DToFGestureRecognizer()

    # Simulated data streaming in at 5 FPS
    # A perfect "Swipe Left" simulation (Hand moving from right cols to left cols)
    simulated_stream = [
        # Frame 1: Hand appears on the right side
        np.array([[25]*5 + [15]*3 for _ in range(8)]), 
        # Frame 2: Hand moves to the center-right
        np.array([[25]*3 + [14]*3 + [25]*2 for _ in range(8)]), 
        # Frame 3: Hand moves to center-left
        np.array([[25]*2 + [15]*3 + [25]*3 for _ in range(8)]), 
        # Frame 4: Hand moves to the far left
        np.array([[14]*3 + [25]*5 for _ in range(8)])  
    ]

    print("Streaming frames into the algorithm...")
    for i, frame in enumerate(simulated_stream):
        gesture = recognizer.process_frame(frame)
        print(f"Frame {i+1}: Result -> {gesture}")

    print('To start gesture, run the file tmf8829_zeromq_client.py')

    time.sleep(4)
