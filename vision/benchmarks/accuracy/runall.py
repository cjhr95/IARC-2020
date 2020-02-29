"""
Run time benchmarks.

Process
-------
files = [filename for filename in 'times/' if 'bench' in filename]
benchmarks = [class for class in filenames if 'Accuracy' in class_name]

for benchmark in benchmarks:
    instance = benchmark()

    try: instance.setup()

    for method in benchmark if 'accuracy' in method_name:
        for title, parameters in benchmark.PARAMETERS.items():
            accuracy(method(instance, *parameters))

            log(benchmark, method, title, accuracy)

Suggested Parameter Defaults
----------------------------
Resolution = (1280, 720)
Noise SD = 0
N Objects = 0
"""
import os
import json
import numpy as np
import pandas as pd

from accuracy import modules


def accuracy_boundingbox(filename, method, instance):
    """
    Calculate how far off each bounding box was

    Returns
    -------
    float Mean squared error between annotation and given.
    """
    ## Read color and depth images

    ## Read annotation data
    prefix = 'vision' if os.path.isdir("vision") else ''
    img_folder = os.path.join(prefix, 'vision_images', 'boat')
    annotation_folder = os.path.join(img_folder, 'Annotations')

    annotations = {filename: lxml.etree.parse(os.path.join(annotation_folder, filename)).getroot() for filename in os.listdir(annotation_folder)}


    output = method(instance, color_image, depth_image)

    ## Calculate error
    # what if output misses box?
    # better accuracy mectric for this?
THRESHOLD = 5
        ## Check accuracy of text detector
        for _, annotation in annotations.items():
            filename = annotation.find('path').find('value').text

            with self.subTest(i=filename):
                img_path = os.path.join(img_folder, filename)
                image = cv2.imread(img_path)

                assert image.shape, f"Failed to read {img_path}!"

                bounding_boxes = detect_russian_word(image)

                accuracy = 0

                for value in annotation.findall('object'):
                    annotation_bounding_box = value.find('bndbox')

                    ax1, ay1, ax2, ay2 = [int(annotation_bounding_box.find(param).text) for param in ['xmin', 'ymin', 'xmax', 'ymax']]

                    for bounding_box in bounding_boxes:
                        ## Get x's and y's from bounding box
                        X, Y, Z = [], [], []
                        for x, y in bounding_box.vertices:
                            X.append(x)
                            Y.append(y)

                        X, Y = np.unique(X), np.unique(Y)
                        bx1, by1, bx2, by2 = min(X), min(Y), max(X), max(Y)

                        ## see if bx1, by1,... within +/- threshold of each ax1, ...

                        x1_close = bx1 - THRESHOLD <= ax1 <= bx1 + THRESHOLD
                        y1_close = by1 - THRESHOLD <= ay1 <= by1 + THRESHOLD
                        x2_close = bx2 - THRESHOLD <= ax2 <= bx2 + THRESHOLD
                        y2_close = by2 - THRESHOLD <= ay2 <= by2 + THRESHOLD

                        if all((x1_close, y1_close, x2_close, y2_close)):
                            accuracy += 1

                    accuracy /= len(annotation.findall('object'))
                    print(f"{filename}: {accuracy * 100:.2f}%")

    error = 0

    return error


def accuracy_boolean():
    pass


classification_map = {
    'location': accuracy_boundingbox,
    'in_frame': accuracy_boolean,
}

if __name__ == '__main__':
    benchmarks = {}

    ## Find time benchmarks in modules
    for module in modules:
        for key, value in module.__dict__.items():
            if key[:4] == 'Accuracy':
                benchmarks.update({key: value})

        ## Read benchmark configuration
        with open(os.path.join('..', 'vision_images', module.__dict__['IMG_FOLDER'], 'benchmark.json')) as file:
            benchmark_config = json.load(file)
        print(benchmark_config)

        classification = benchmark_config['classification']
        types = benchmark_config['types']
        parameters = benchmark_config['data']

        ## Run benchmarks
        output = pd.DataFrame(columns=['class', 'method', 'type', 'filename', 'result'])

        for b_name, benchmark in benchmarks.items():
            b_instance = benchmark()

            try:
                b_instance.setup()
            except AttributeError as e:
                print(f"No setup method found for {b_name}.")

            for m_name, method in benchmark.__dict__.items():
                if 'accuracy_' not in m_name or not callable(method):
                    continue

                for filename, p_type in parameters.items():
                    try:
                        result = classification_map[classification](filename, method, )

                    except Exception as e:
                        print(f"{b_name}.{m_name}: {p_name} error: {e}")

                        output.loc[len(output)] = [b_name, m_name, p_type, filename, np.nan]
                    else:
                        print(f"{b_name}.{m_name}: {p_name} {time:.5f}s")

                        output.loc[len(output)] = [b_name, m_name, p_type, filename, result]

    print(output.head(15))
    # output.to_csv('', index=False)

    print()
