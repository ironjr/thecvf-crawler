import os


def remove_empty_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                if os.path.getsize(path) == 0:
                    print("[INFO] Detected empty file : {}".format(path))
                    os.remove(path)
            except Exception as e:
                print(e)
