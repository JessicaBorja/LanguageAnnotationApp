import argparse
import glob
import json
import os

import cv2
import numpy as np


class DataManager:
    def __init__(self, data_root: str, n_frames: int, grip_pt_h: bool = False) -> None:
        super().__init__()
        self.media_dir = './webapp/static/'
        for cam in ["gripper", "static"]:
            make_dir = os.path.join(self.media_dir, "%s_cam" % cam)
            os.makedirs(make_dir, exist_ok=True)
        self.save_data_dir = './webapp/static/'
        self.data_path = data_path
        self.n_frames = n_frames
        self.grip_pt_h = grip_pt_h
        self.n_seq = 150
        _json_data = self.read_json()
        if _json_data is None:
            self.data = self.read_data(data_root)
        else:
            self.data = _json_data
        # self.create_add_videos()
        self._c = 1

    def read_json(self):
        data_filename = os.path.join(self.save_data_dir, "data.json")
        data = None
        if os.path.isfile(data_filename):
            with open(data_filename, "r") as read_file:
                data = json.load(read_file)
        else:
            print("Could not find previous data: %s" % data_filename)
        return data

    def save_json(self, data):
        data_filename = os.path.join(self.save_data_dir, "data.json")
        with open(data_filename, "w") as fout:
            json.dump(data, fout, indent=2)

    def create_tmp_video(self, start, end, dir, id):
        video_tag = "tmp_%d.webM" % id
        # if(os.path.isfile(os.path.join(self.tmp_dir, video_tag))):
        #     return video_tag

        start_idx = self.filename_to_idx(start)
        end_idx = self.filename_to_idx(end)
        gripper_imgs, static_imgs = [], []
        for i in range(start_idx, end_idx + 1):
            frame_i = self.idx_to_filename(i)
            filename = os.path.join(dir, frame_i)
            imgs = self.extract_imgs(filename)
            gripper_imgs.append(imgs["gripper"])
            static_imgs.append(imgs["static"])
        
        self.make_video(gripper_imgs, video_name=video_tag, cam="gripper")
        self.make_video(static_imgs, video_name=video_tag, cam="static")
        return video_tag
   
    def make_video(self, seq_imgs, fps=80, video_name="v", cam="static"):
        folder_path = os.path.join(self.media_dir, "%s_cam" % cam)
        video_path = os.path.join(folder_path, video_name)

        w, h = seq_imgs[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc("V", "P", "8", "0")
        video = cv2.VideoWriter(video_path, fourcc, fps, (w, h))  # 30 fps
        print("writing video to %s" % video_path)
        for img in seq_imgs:
            video.write(img[:, :, ::-1])
        cv2.destroyAllWindows()
        video.release()

    def extract_imgs(self, filename):
        data = np.load(filename, allow_pickle=True)
        imgs = {}
        for cam in ["gripper", "static"]:
            img = data["rgb_%s" % cam]
            img = cv2.resize(img, (300, 300))
            imgs[cam] = img
        # cv2.imshow("static", img[:, :, ::-1])  # W, H, C
        # cv2.waitKey(1)
        return imgs

    def filename_to_idx(self, filename):
        return int(filename.split("_")[-1][:-4])

    def idx_to_filename(self, idx):
        return "frame_%06d.npz" % idx

    def read_data_unprocessed(self, play_data_path):
        '''
            play_data_path -> day -> time
            _data:(list)
                - {'indx': [start_filename, end_filename],
                   'dir': directory of previous files,
                   'n_frames': end_frame - start_frame}
        '''
        # Get all posible initial_frames
        initial_frames = []
        date_folder = glob.glob("%s/*" %play_data_path, recursive=True)
        for path in date_folder:
            data_path = os.path.basename(path)

            # Get files in subdirectory
            time_folder = glob.glob("%s/*" % path, recursive=True)
            for dir in time_folder:
                files = glob.glob("%s/**/frame_*.npz" %dir, recursive=True)
                files.sort()
                indices = range(0, len(files) - self.n_frames, self.n_frames//2)
                files = [files[i] for i in indices]
                files = files[:-self.n_frames]
                initial_frames.extend(files)
        
        # Select n_seq random sequences
        n_seq = min(len(initial_frames), self.n_seq)
        initial_frames = np.random.choice(initial_frames, size=n_seq, replace=False)
        frames_info = {}
        _data = []
        for frame_dir in initial_frames:
            head, start_filename = os.path.split(frame_dir)
            frame_idx = self.filename_to_idx(start_filename)
            end_frame_idx = frame_idx + self.n_frames
            end_filename = self.idx_to_filename(end_frame_idx)
            frames_info = {'indx': [start_filename, end_filename],
                           'dir': head,
                           'n_frames': self.n_frames}
            _data.append(frames_info)
        self.save_json(_data)
        return _data

    def read_data_preprocessed(self, play_data_path):
        '''
            play_data_path -> day -> time
            _data:(list)
                - {'indx': [start_filename, end_filename],
                   'dir': directory of previous files,
                   'n_frames': end_frame - start_frame}
        '''
        # Get all posible initial_frames
        initial_frames = []
        date_folder = glob.glob("%s/*" % play_data_path, recursive=True)
        for path in date_folder:
            data_path = os.path.basename(path)

            # Get files in subdirectory
            time_folder = glob.glob("%s/*" % path, recursive=True)
            for dir in time_folder:
                files = glob.glob("%s/**/frame_*.npz" % dir, recursive=True)
                files.sort()
                indices = range(0, len(files) - self.n_frames, self.n_frames // 2)
                files = [files[i] for i in indices]
                files = files[: -self.n_frames]
                initial_frames.extend(files)

        # Select n_seq random sequences
        n_seq = min(len(initial_frames), self.n_seq)
        initial_frames = np.random.choice(initial_frames, size=n_seq, replace=False)
        frames_info = {}
        _data = []
        for frame_dir in initial_frames:
            head, start_filename = os.path.split(frame_dir)
            frame_idx = self.filename_to_idx(start_filename)
            end_frame_idx = frame_idx + self.n_frames
            end_filename = self.idx_to_filename(end_frame_idx)
            frames_info = {"indx": [start_filename, end_filename], "dir": head, "n_frames": self.n_frames}
            _data.append(frames_info)
        self.save_json(_data)
        return _data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_root", type=str, default="data", help="directory where raw dataset is allocated")
    args = parser.parse_args()
    data_manager = DataManager(args.dataset_root, n_frames=128, grip_pt_h=False)
