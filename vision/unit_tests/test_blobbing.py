import unittest
import os
import sys
import json
import cv2

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from vision.blob.blobfind import BlobFinder, import_params


class TestBlobbing(unittest.TestCase):
    def test_finding_blobs(self):
        """
        Tests that the expected number of blobs is found

        Settings
        --------
        expected_blobs: dict{string: int}
            number of expected blobs (value) to be found in each image (key)

        Returns
        -------
        list[bool]
            whether the expected number of blobs in each image equals the detected number of blobs
        """
        expected_blobs = {
            "apple.jpg": 1,
            "legos.jpg": 30,
            "MyBeach.png": 1,
            "oranges.png": 1,
            "sampleobj.png": 1
        }
        prefix = 'vision' if os.path.isdir("vision") else ''

        config_filename = os.path.join(prefix, 'blob', 'config.json')
        with open(config_filename, 'r') as config_file:
            raw_config = json.load(config_file)

        config = import_params(raw_config)

        for filename, expected in expected_blobs.items():
            with self.subTest(i=filename):
                img_filename = os.path.join(prefix, 'vision_images', 'blob', filename)
                img_file = cv2.imread(img_filename)

                detector = BlobFinder(img_file, params=config)
                bounding_boxes = detector.find()

                self.assertEqual(len(bounding_boxes), expected, msg=f"Expected {expected} blobs, found {len(bounding_boxes)} in image {filename}")


if __name__ == '__main__':
    unittest.main()