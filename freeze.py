import os
import shutil
import cv2
import random
import json
import argparse

'''
Creates a fresh directory and deletes if it exists
'''
def create_fresh_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return path


'''
Extracts frames from a video, saves the frames and returns the metadata
'''
def extract_frames(video_path, output_path, num_frames, file_name, delimiter):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_indices = random.sample(range(total_frames), num_frames)
    frame_timestamps = []
    for i in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
            frame_timestamps.append(timestamp)
            cv2.imwrite(f"{output_path}/{file_name}{delimiter}{i}.jpg", frame)
        else:
            break
    cap.release()
    return {'frame_rate': frame_rate,
            'chosen_frames': frame_indices,
            'chosen_timestamps': frame_timestamps
            }

'''
Creates the metadata file for a video
'''
def popualate_stats(output_path, file_name, frame_rate, frame_timestamp_map):
    stats_fname = os.path.join(output_path, f'{file_name}.json')
    stats = {'frame_rate': frame_rate}
    stats.update(frame_timestamp_map)
    with open(stats_fname, 'w') as outfile:
        json.dump(stats, outfile)

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Add arguments
parser.add_argument('--videos-source', '-s', type=str, required=True, help='The folder which contains all the videos')
parser.add_argument('--output-path', '-o', type=str, required=True, help='The path that will save two directories, the frames and the metadata')
parser.add_argument('--frames-per-video', '-n', type=int, default=10, help='The number of frames to extract from each video')
parser.add_argument('--random-seed', '-r', type=int, default=None, help='A random seed that is added to the random extractor')
parser.add_argument('--verbose', '-v', action=argparse.BooleanOptionalAction, default=True, help='Verbose means to print progress. Setting to false stays silent')

if __name__ == '__main__':
    # Parse arguments
    args = parser.parse_args()

    vids_source_path =args.videos_source
    output_path = args.output_path
    random_seed = args.random_seed
    num_frames = args.frames_per_video
    verbose = args.verbose

    delimiter = '@'

    frames_output_path = create_fresh_dir(os.path.join(output_path, 'frames'))
    stats_path = create_fresh_dir(os.path.join(output_path, 'metadata'))


    vids_fnames = os.listdir(vids_source_path)
    vids_fpaths = [os.path.join(vids_source_path, filename) for filename in vids_fnames]
    vids_fnames = [os.path.splitext(os.path.basename(filename))[0] for filename in vids_fnames]

    for vid_name in vids_fnames:
        assert delimiter not in vid_name, f"File name {vid_name} can't have {delimiter} character."

    random.seed(random_seed)

    if verbose:
        print('Starting\n')
    for i, (filepath, filename) in enumerate(zip(vids_fpaths, vids_fnames)):
        output = extract_frames(
            video_path=filepath,
            file_name=filename,
            output_path=frames_output_path,
            num_frames=num_frames,
            delimiter=delimiter
        )
        
        popualate_stats(stats_path, file_name=filename, frame_rate=output['frame_rate'], frame_timestamp_map={frame:timestamp for frame, timestamp in zip(output['chosen_frames'], output['chosen_timestamps'])})
        if (verbose):
            print(f'Freezed {i+1} of {len(vids_fnames)}...')

    if (verbose):
        print('All videos have been frozen 🥶')
