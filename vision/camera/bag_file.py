"""
The BagFile class is a child class of the camera, designed to be used for pre-recorded .bag files
"""
import cv2
import numpy as np
import pyrealsense2 as rs
try:
    from vision.camera.template import Camera
except ImportError:
    from template import Camera
try:
    from vision.common.take_picture import save_camera_frame
except ImportError:
    from common.take_picture import save_camera_frame


class BagFile(Camera):
    """
    Creates a bag file reader object

    Parameters
    ----------
    screen_width: number
        Resolution width of the pre-recorded .bag file
    screen_height: number
        Resolution height of the pre-recorded .bag file
    frame_rate: number
        Framerate of the pre-recorded .bag file
    filename: str
        Name of .bag file to read.
        Driver should find this by parsing arguments
    """
    def __init__(self, screen_width, screen_height, frame_rate, filename, **kwargs):
        super().__init__(screen_width, screen_height, frame_rate)

        self.filename = filename

        self.pipeline = rs.pipeline()

        # Create a config object
        self.config = rs.config()
        # Tell config that we will use a recorded device from file
        # to be used by the pipeline through playback.
        rs.config.enable_device_from_file(self.config, self.filename)

    def __iter__(self):
        """
        Iterate through each frame in the bag file.
        NOTE: This loops through the video continuously.

        Returns
        -------
        depth image[1 channel]: numpy array
        color image[3 channel]: numpy array
            in RGB format
        """
        # Start streaming from file
        self.pipeline.start(self.config)

        align_to = rs.stream.color
        align = rs.align(align_to)

        while True:
            # returns the next color/depth frame
            frames = self.pipeline.wait_for_frames()

            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            # aligned_depth_frame is a 640x480 depth image
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image = color_image[:, :, ::-1]  # shifts colors back to normal

            yield depth_image, color_image

    def display_in_window(self, clipping=False):
        """
        Displays the depth/color image streams on repeat, separately, in one window

        Parameters
        -------
        clipping: boolean
            defaults to false, can be set true to remove data from the images
            beyond a given distance from the camera
        """
        for depth_image, color_image in self:
            # Remove background - Set pixels further than clipping_distance to grey
            grey_color = 153
            depth_image_3d = np.dstack((depth_image, depth_image, depth_image))

            # render depth/color images
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03),
                cv2.COLORMAP_JET)

            if clipping:
                bg_removed = np.where((depth_image_3d <= 0), grey_color, color_image)
                images = np.hstack((bg_removed, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))

            cv2.namedWindow('Depth/Color Stream', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Depth/Color Stream', self.width, int(self.height / 2))
            cv2.imshow('Depth/Color Stream', images)

            key = cv2.waitKey(1)

            if key == ord('c'):
                save_camera_frame(depth_image, color_image)

            # if pressed 'q' or escape (27) exit program
            if key == ord('q') or key == 27 or cv2.getWindowProperty("Depth/Color Stream", 0) == -1:
                cv2.destroyAllWindows()
                break

if __name__ == '__main__':
    import sys
    BagFile(720, 1080, 0, sys.argv[1]).display_in_window()
