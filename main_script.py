import os
import multiprocessing
from subprocess import run

def print_intro():
    print("该软件由B站花开富贵doge制作")
    print("https://space.bilibili.com/495772936")
    print(" ")

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

def main():
    print_intro()
    print("选择模式:")
    print("1. 路径模式")
    print("2. 文件模式（处理 'video' 文件夹中的所有 MP4 文件）")
    mode = input("请输入选项 (1/2): ")
    if mode == '1':
        while True:
            video_path = input("请输入MP4视频文件的路径：")
            video_path = validate_and_normalize_path(video_path)
            if video_path:
                video_paths = [video_path]
                break
            else:
                print("请输入有效的路径。")
    elif mode == '2':
        folder_path = os.path.join(os.getcwd(), 'video')
        if not os.path.exists(folder_path):
            print(f"文件夹 {folder_path} 不存在，程序终止。")
            return
        video_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.mp4')]
        if not video_paths:
            print(f"文件夹 {folder_path} 中没有找到 MP4 文件，程序终止。")
            return
    else:
        print("无效选择，程序终止。")
        return

    while True:
        print("选择压缩比例:")
        print("1. 4:3 (1.33)")
        print("2. 16:9 (1.78)")
        print("3. 自定义比例")
        print("4. 计算宽高比")
        choice = input("请输入选项 (1/2/3/4): ")
        if choice == '1':
            target_aspect_ratio = 4 / 3
            break
        elif choice == '2':
            target_aspect_ratio = 16 / 9
            break
        elif choice == '3':
            custom_ratio = float(input("请输入自定义宽高比（例如 1.78 代表 16:9）："))
            target_aspect_ratio = custom_ratio
            break
        elif choice == '4':
            calculate_ratio()
        else:
            print("无效选择，请重试。")

    process_script_path = get_resource_path('process_script.py')
    run(["python", process_script_path, str(target_aspect_ratio)] + video_paths)

def get_resource_path(relative_path):
    import sys
    import os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
