import numpy as np
import tensorflow as tf
from tensorflow import keras
from .preprocess import prepare_image
import matplotlib.pyplot as plt
from config.bigquery import BigQuery

import cv2

"""
## Implementing utility functions
Bounding boxes can be represented in multiple ways, the most common formats are:
- Storing the coordinates of the corners `[xmin, ymin, xmax, ymax]`
- Storing the coordinates of the center and the box dimensions
`[x, y, width, height]`
Since we require both formats, we will be implementing functions for converting
between the formats.
"""




def read_image(image_path, inference_model, int2str):
    png_string = tf.io.read_file(image_path)
    img = tf.image.decode_png(png_string, channels=3)
    image = tf.cast(img, dtype=tf.float32)
    input_image, ratio = prepare_image(image)
    detections = inference_model.predict(input_image)
    num_detections = detections.valid_detections[0]
    class_names = [
            int2str(int(x)) for x in detections.nmsed_classes[0][:num_detections]
    ]
    visualize_detections(
            image,
        detections.nmsed_boxes[0][:num_detections] / ratio,
        class_names,
        detections.nmsed_scores[0][:num_detections],
    )

def visualize_detections(
    image, boxes, classes, scores, figsize=(7, 7), linewidth=1, color=[0, 0, 1]
):
    """Visualize Detections"""
    image = np.array(image, dtype=np.uint8)
    plt.figure(figsize=figsize)
    plt.axis("off")
    plt.imshow(image)
    ax = plt.gca()
    for box, _cls, score in zip(boxes, classes, scores):
        text = "{}: {:.2f}".format(_cls, score)
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        patch = plt.Rectangle(
            [x1, y1], w, h, fill=False, edgecolor=color, linewidth=linewidth
        )
        ax.add_patch(patch)
        ax.text(
            x1,
            y1,
            text,
            bbox={"facecolor": color, "alpha": 0.4},
            clip_box=ax.clipbox,
            clip_on=True,
        )
    plt.show()
    return ax

def read_video(video_path, inference_model, int2str):
    bigquery = BigQuery(None)
    player = cv2.VideoCapture(video_path)

    frame_width = int(player.get(3))
    frame_height = int(player.get(4))
 
    # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
    output = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_height))
    
    count = 0

    while player.isOpened():
        
        ret, frame = player.read()
        #cv2.imshow("video", frame)
        #error on cast
        
        if(ret):     
            # adding filled rectangle on each frame
            # add text to retangle
            image = tf.cast(frame, dtype=tf.float32)
            #print(image)
            input_image, ratio = prepare_image(image)
            detections = inference_model.predict(input_image)
            num_detections = detections.valid_detections[0]
            class_names = [
                    int2str(int(x)) for x in detections.nmsed_classes[0][:num_detections]
            ]
            for box, _cls, score in zip(detections.nmsed_boxes[0][:num_detections] / ratio, class_names, detections.nmsed_scores[0][:num_detections]):
                text = "{}: {:.2f}".format(_cls, score)
                texttotal = "agamotto_total_count: {:.2f}".format(num_detections)
                x1, y1, x2, y2 = box
                w, h = x2 - x1, y2 - y1
                cv2.rectangle(frame, (x1, y1), (x2, y2),
                          (0, 255, 0), 1)
                cv2.putText(frame, text, (x1, y1-10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (36,255,12), 1)
                cv2.putText(frame, texttotal, (100, 100), cv2.FONT_HERSHEY_COMPLEX, 0.9, (36,255,12), 2)
                
            bigquery.insert_row(num_detections)  
            # writing the new frame in output
            output.write(frame)
            count += 30 # i.e. at 30 fps, this advances one second
            player.set(cv2.CAP_PROP_POS_FRAMES, count)
            #cv2.imshow("output", frame)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
        else:
            player.release()
            break
            
    cv2.destroyAllWindows()
    output.release()
    player.release()