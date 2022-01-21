# Code for "TSM: Temporal Shift Module for Efficient Video Understanding"
# arXiv:1811.08383
# Ji Lin*, Chuang Gan, Song Han
# {jilin, songhan}@mit.edu, ganchuang@csail.mit.edu

import os
import threading

NUM_THREADS = 2
VIDEO_ROOT = 'dribbing-testvideo'         # Downloaded webm videos
FRAME_ROOT = 'dribbling-frames'  # Directory for extracted frames


def split(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def extract(video, tmpl='%06d.jpg'):
    # os.system(f'ffmpeg -i {VIDEO_ROOT}/{video} -vf -threads 1 -vf scale=-1:256 -q:v 0 '
    #           f'{FRAME_ROOT}/{video[:-5]}/{tmpl}')
    cmd = 'ffmpeg -i \"{}/{}\" -threads 1 -vf scale=-1:256 -q:v 0 \"{}/{}/%06d.jpg\"'.format(VIDEO_ROOT, video,
                                                                                             FRAME_ROOT, video[:-4])
    os.system(cmd)


def target(video_list):
    print(video_list)
    for video in video_list:
        # print(video[:-4])
        # print(video.replace(".mp4", ""))
        if not os.path.exists(os.path.join(FRAME_ROOT, video[:-4])):
            os.makedirs(os.path.join(FRAME_ROOT, video[:-4]))
            extract(video)

def split_list(l, n):
    for idx in range(0, len(l), n):
        yield l[idx:idx+n]


if __name__ == '__main__':
    if not os.path.exists(VIDEO_ROOT):
        raise ValueError('Please download videos and set VIDEO_ROOT variable.')
    if not os.path.exists(FRAME_ROOT):
        os.makedirs(FRAME_ROOT)

    video_list = os.listdir(VIDEO_ROOT)
    # part = list(split_list(video_list, 20000))
    part = list(split_list(video_list, 10))
    print(part)
    # for i in range(len(part)):
    splits = list(split(part[0], NUM_THREADS))
    print("====")
    print(splits)

    threads = []
    for i, split in enumerate(splits):
        thread = threading.Thread(target=target, args=(split,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
