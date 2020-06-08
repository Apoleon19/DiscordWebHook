import os
import requests
import logging.config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.config'))
logger = logging.getLogger('main')


def split_files_by_size(files_data, files_data_size, max_size=8192000, max_split_size=10):
    files_splits = []
    last_file_index = 0
    current_size_data = 0

    while files_data_size != current_size_data or current_size_data > files_data_size:
        current_files_split = dict()
        current_split_size = 0

        files_to_check = files_data[last_file_index:]
        for counter, file in enumerate(files_to_check):
            if (file['size'] + current_split_size) < max_size and counter < max_split_size:
                current_split_size += file['size']
                current_files_split.update({file['name']: (file['name'], file['file'])})
            else:
                last_file_index += counter
                break

        files_splits.append(current_files_split)
        current_size_data += current_split_size
    return files_splits


def load_files_from_directory(directory, index=0, max_files=999):
    directory_path = os.path.join(BASE_DIR, directory)
    files_list = [file for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]
    files_list_loaded = []
    files_size = 0
    for index, file_name in enumerate(files_list[index:]):
        if len(files_list_loaded) < max_files:
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'rb') as f:
                file = f.read()
                files_list_loaded.append({'file': file, 'name': file_name, 'size': len(file)})
                files_size += len(file)
        else:
            break
    return files_list_loaded, files_size, index


def get_directory_files_size(directory):
    directory_path = os.path.join(BASE_DIR, directory)
    files_size = [os.path.getsize(os.path.join(directory_path, file)) for file in os.listdir(directory_path)]
    return sum(files_size)


def download_files(urls: list):
    downloaded_files = []
    files_size = 0
    for url in urls:
        r = requests.get(url, stream=True)
        file_name = url.split('/')[-1]
        file = r.raw.read()
        try:
            r.raise_for_status()
            downloaded_files.append({'file': file, 'name': file_name, 'size': len(file)})
            files_size += len(file)
        except requests.exceptions.HTTPError as e:
            logger.error(e)
    return downloaded_files, files_size
