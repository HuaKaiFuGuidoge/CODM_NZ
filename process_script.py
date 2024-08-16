import os
import moviepy.editor as mp
from PIL import Image
from tqdm import tqdm
from multiprocessing import Manager, Pool, cpu_count
import time

Image.ANTIALIAS = Image.LANCZOS

def validate_and_normalize_path(path):
    try:
        path = path.strip('\"\'')
        normalized_path = os.path.normpath(path)
        if os.path.exists(normalized_path):
            return normalized_path
        else:
            print(f"路径错误：{path} 不存在。")
            return None
    except Exception as e:
        print(f"路径处理错误：{str(e)}")
        return None

def calculate_ratio():
    while True:
        user_input = input("请输入想要计算的宽高比（例如16:9），或输入 'esc' 来返回主菜单：")
        if user_input.lower() == "esc":
            break
        try:
            width, height = map(float, user_input.split(':'))
            ratio = width / height
            print(f"宽高比 {width}:{height} 的小数表示为 {ratio:.2f}")
        except ValueError:
            print("输入格式错误，请输入有效的宽高比，例如 16:9。")

def process_video(video_path, target_aspect_ratio, progress_dict):
    video = mp.VideoFileClip(video_path)
    target_width = video.size[1] * target_aspect_ratio
    resized_video = video.resize(newsize=(int(target_width), video.size[1]))
    total_frames = int(resized_video.fps * resized_video.duration)

    def update_frame(get_frame, t):
        if 'total' in progress_dict and progress_dict['total'] != total_frames:
            progress_dict['total'] = total_frames
        if 'processed' in progress_dict:
            progress_dict['processed'] += 1
        return get_frame(t)

    resized_video = resized_video.fl(update_frame, apply_to=['mask', 'audio'])
    output_path = f"output_{os.path.basename(video_path)}"
    resized_video.write_videofile(output_path, codec="libx264")
    print(f"视频 {video_path} 已成功调整并保存到 {output_path}")

def process_videos(video_paths, target_aspect_ratio, use_multi_core):
    if use_multi_core:
        num_cores = cpu_count()
        print(f"检测到 {num_cores} 个核心。")

        with Manager() as manager:
            progress_dict = manager.dict()
            progress_dict['total'] = 0
            progress_dict['processed'] = 0
            video_count = len(video_paths)

            with Pool(num_cores) as pool:
                pool.starmap(process_video,
                             [(video_paths[i], target_aspect_ratio, progress_dict) for i in range(video_count)])

            pbar = tqdm(total=progress_dict['total'], desc="总体处理进度", unit="帧", dynamic_ncols=True, ncols=100)
            while progress_dict['processed'] < progress_dict['total']:
                pbar.update(progress_dict['processed'] - pbar.n)
                time.sleep(0.1)
            pbar.close()
    else:
        for video_path in video_paths:
            process_video(video_path, target_aspect_ratio, {'position': 0})

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("参数错误，请提供目标宽高比。")
        sys.exit(1)

    target_aspect_ratio = float(sys.argv[1])
    video_paths = sys.argv[2:]
    if not video_paths:
        print("没有输入视频文件路径，程序终止。")
    else:
        if len(video_paths) > 1:
            use_multi_core = input("是否使用多核心处理？(y/n): ").strip().lower() == 'y'
        else:
            use_multi_core = False

        process_videos(video_paths, target_aspect_ratio, use_multi_core)
