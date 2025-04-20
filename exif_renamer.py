# search for app parameters
import glob
import os
import pathlib
import sys

import exiftool

PICTURES_DATE_TAG = "EXIF:DateTimeOriginal"
VIDEOS_DATE_TAG = "MakerNotes:DateTimeOriginal"
SHUTTER_COUNT_TAG = "MakerNotes:ShutterCount"
FILENAME_TAG = "SourceFile"

if len(sys.argv) != 2:
    print("usage:\nexif_rename path_2_scan")
    quit(-1)

path_2_scan = sys.argv[1]
if not path_2_scan.endswith("/"):
    path_2_scan += "/"
print(f"path to scan: {path_2_scan}")


def is_media_file(filename):
    supported_types = {".jpg", ".jpeg", ".nef", ".heic", ".hif", ".mov", ".m4v", ".avi"}
    filepath = pathlib.Path(filename)
    if not filepath.is_file():
        return False

    if filepath.suffix.lower() not in supported_types:
        return False

    if "DSC" in filepath.name:
        return True

    if "IMG" in filepath.name:
        return True

    return False


def is_cropped(filename):
    return "_recadree" in filename or "_retouchee" in filename


media_files = [filename for filename in glob.glob(path_2_scan + "**", recursive=True) if is_media_file(filename)]
total_files = len(media_files)

if total_files == 0:
    print("\nNo file to rename.\nDone.")
    quit(-2)

with exiftool.ExifToolHelper() as et:
    print(f'\rscanning files ({total_files}) tags')
    files_tags = et.get_tags(media_files, tags=[FILENAME_TAG, PICTURES_DATE_TAG, VIDEOS_DATE_TAG, SHUTTER_COUNT_TAG])
    print("Done.")
    counter = 0
    for current_file_tags in files_tags:
        infos_keys = current_file_tags.keys()
        old_name = current_file_tags[FILENAME_TAG]
        filepath = pathlib.Path(old_name)
        media_datetime = None
        if PICTURES_DATE_TAG in infos_keys:
            media_datetime = current_file_tags[PICTURES_DATE_TAG]
        elif VIDEOS_DATE_TAG in infos_keys:
            media_datetime = current_file_tags[VIDEOS_DATE_TAG]
        else:
            continue
        new_name = media_datetime.replace(":", "").replace(" ", "_")
        if SHUTTER_COUNT_TAG in infos_keys:
            new_name += f"_{current_file_tags[SHUTTER_COUNT_TAG]}"

        new_name = f"{filepath.parent}/{new_name}{'_recadree' if is_cropped(old_name) else ''}{filepath.suffix.lower()}"

        if os.path.exists(filepath.name + "AAE"):
            print("rename AAE matching file")
        elif os.path.exists(filepath.name + "aae"):
            print("rename aae matching file")

        # print(f"rename: {old_name} = {new_name}")
        counter += 1
        print(f'\r{counter}/{total_files} => {new_name}')
        os.rename(old_name, new_name)
print("\nDone.")
