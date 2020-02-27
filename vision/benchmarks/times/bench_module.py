"""
For testing all module algorithms.
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import unittest
import cv2

from vision.module.in_frame import ModuleInFrame as mif
#from vision.module.detector import ModuleKMeans as mkm


class TimeModuleInFrame(unittest.TestCase):
    """
    Testing module.in_frame functionality.
    """
    def test_ModuleInFrame(self):
        """
        Testing ModuleInFrame

        Returns
        -------
        ndarray[bool] which images the module was detected in
        """

        results = []
        expected_results = {
            "Block1.jpg" : True,
            "Block2.jpg" : True,
            "Block3.jpg" : True,
            "Block4.jpg" : True
        }
        for picname in expected_results.keys():
            with self.subTest(i=picname):
                picpath = os.path.join('vision_images', 'module', picname)

                image = cv2.imread(picpath)


                if image is None:
                    raise FileNotFoundError(f"Could not read {picpath}!")

                results.append(mif(image))

        self.assertListEqual(results, list(expected_results.values()))


if __name__ == '__main__':
    unittest.main()
