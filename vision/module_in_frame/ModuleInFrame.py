"""
This file contains the ModuleInFrame function to detect if the module is in an image
"""

import cv2
import numpy as np

def ModuleInFrame(img):
    """
    Determines if the Module is in frame

    Parameters
    ----------
    img: numpy array
        The image stored in a numpy array.

    Returns
    -------
    bool: true if the module is in the frame and false if not in the frame
    """

    # Ignore numpy warnings
    np.seterr(all="ignore")

    # Remove depth channel
    img = img[:, :, :3]

    # Grayscale
    gray = cv2.cvtColor(src=img, code=cv2.COLOR_RGB2GRAY)

    # Guassian Blur
    blur = cv2.GaussianBlur(src=gray, ksize=(5,5), sigmaX=0)

    # Laplacian Transform
    laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=3)
    laplacian = np.uint8(laplacian)

    # Hough Circle Detection
    circles = cv2.HoughCircles(image=laplacian, method=cv2.HOUGH_GRADIENT, dp=1, minDist=8, param1=50, param2=40, minRadius=0, maxRadius=50)
    circles = np.uint16(circles)

    # Resize circles into 2d array
    circles = np.reshape(circles, (np.shape(circles)[1], 3))

    # Finding slopes between the circles
    slopes = []
    for x, y, r in circles:
        for iX, iY, iR in circles:
            m = (iY - y) / (iX - x)
            # slope must be non-infinite and can't be between the same circle
            if (not np.isnan(m)) and (not np.isinf(m)) and (x != iX and y != iY):
                slopes.append(m)
    
    # Bucket sorting slopes to group parallels
    slopes = np.array(np.abs(slopes))
    upper = np.amax(slopes) 
    lower = np.amin(slopes)
    BUCKET_MODIFIER = 1
    num_buckets = np.int32(upper - lower) * BUCKET_MODIFIER
    buckets, _ = np.histogram(slopes, num_buckets, (lower, upper))
    
    # Determine if any bucket of slopes is big enough
    return any(buckets > 25)