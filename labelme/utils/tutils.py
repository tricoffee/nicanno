import os 

SupportImageType = [".bmp",".png",".jpg",".jpeg"]

def list_files(dir, exts=None):
    "List all files in the current directory"

    fnms = [os.path.join(dir, f).replace("\\","/") for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    if not exts:
        return fnms
    else:
        assert isinstance(exts, (list, tuple)), "exts必须是一个字符串的列表"
        imgs = [fpath for fpath in fnms if fpath.lower().endswith(tuple(exts))]
        return imgs