import numpy as np
import json
import glob
import cv2
import os
import imageio
import base64
import io


class DataManager:
    def __init__(self, data_path, n_frames, grip_pt_h=False) -> None:
        super().__init__()
        self.data_path = data_path
        self.n_frames = n_frames
        self.grip_pt_h = grip_pt_h
        self.n_seq = 150
        _json_data = self.read_json()
        if _json_data is None:
            self.data = self.read_data(data_path)
        else:
            self.data = _json_data
        # self.create_add_videos()
        self._c = 1

    def read_json(self):
        data_filename = './webapp/static/images/data.json'
        data = None
        if os.path.isfile(data_filename):
            with open(data_filename, "r") as read_file:
                data = json.load(read_file)
        else: 
            print("Could not find previous data: %s" % data_filename)
        return data

    def save_json(self, data):
        with open('./webapp/static/images/data.json', 'w') as fout:
            json.dump(data , fout, indent=2)

    def save_gif(self, img_seq, img_name):
        img_dir = './webapp/static/images'
        img_path = '%s/%s.gif' % (img_dir, img_name)
        imageio.mimsave(img_path, img_seq, format='GIF', duration=1)

    def get_gif(self, data_idx):
        seq = self.data[data_idx]
        start, end = seq['indx']
        start_idx = self.filename_to_idx(start)
        end_idx = self.filename_to_idx(end)
        seq_imgs = []
        for i in range(start_idx, end_idx + 1):
            frame_i = self.idx_to_filename(i)
            filename = os.path.join(seq['dir'], frame_i)
            img = self.extract_img(filename)
            seq_imgs.append(img)
        self.save_gif(seq_imgs,"test")
        
        data = io.BytesIO()
        encoded_img_data = base64.b64encode(data.getvalue())
        return encoded_img_data

    def create_tmp_video(self, start, end, dir):
        # seq = self.data[data_idx]
        # start, end = seq['indx']
        start_idx = self.filename_to_idx(start)
        end_idx = self.filename_to_idx(end)
        seq_imgs = []
        for i in range(start_idx, end_idx + 1):
            frame_i = self.idx_to_filename(i)
            filename = os.path.join(dir, frame_i)
            img = self.extract_img(filename)
            seq_imgs.append(img)
        self.make_video(seq_imgs, video_name="tmp")
        # video_tag = "tmp_%d" % self._c
        # self.make_video(seq_imgs, video_name=video_tag)
        # self._c += 1
   
    def make_video(self, seq_imgs, fps=80, video_name="v"):
        media_dir = './webapp/static/images'
        video_path = '%s/%s.webM' % (media_dir, video_name)
        w, h = seq_imgs[0].shape[:2]
        # fourcc = cv2.VideoWriter_fourcc(*'H264')
        fourcc = cv2.VideoWriter_fourcc('V','P','8','0')
        video = cv2.VideoWriter(
                    video_path,
                    fourcc,
                    fps,(w,h))  # 30 fps
        print("writing video to %s" % video_path)
        for img in seq_imgs:
            video.write(img[:, :, ::-1])
        cv2.destroyAllWindows()
        video.release()

    def create_add_videos(self):
        c = 0
        for seq in self.data:
            start, end = seq['indx']
            start_idx = self.filename_to_idx(start)
            end_idx = self.filename_to_idx(end)
            seq_imgs = []
            for i in range(start_idx, end_idx + 1):
                frame_i = self.idx_to_filename(i)
                filename = os.path.join(seq['dir'], frame_i)
                img = self.extract_img(filename)
                seq_imgs.append(img)
            self.make_video(seq_imgs, video_name="tmp%04d.mp4" % c)
        return

    def extract_img(self, filename):
        data = np.load(filename, allow_pickle=True)
        img = data["rgb_static"]
        img = cv2.resize(img, (300, 300))
        # cv2.imshow("static", img[:, :, ::-1])  # W, H, C
        # cv2.waitKey(1)
        return img

    def filename_to_idx(self, filename):
        return int(filename.split('_')[-1][:-4])

    def idx_to_filename(self, idx):
        return 'frame_%06d.npz' % idx

    def read_data(self, play_data_path):
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
                files = files[:-self.n_frames]
                initial_frames.extend(files)
        
        # Select n_seq random sequences
        initial_frames = np.random.choice(initial_frames, size=self.n_seq, replace=False)
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


if __name__== '__main__':
    data_path = "/mnt/ssd_shared/Users/Jessica/Documents/Thesis_ssd/datasets/unprocessed/real_world/tabletop"
    data_manager = DataManager(data_path,
                               n_frames=128,
                               grip_pt_h=False)