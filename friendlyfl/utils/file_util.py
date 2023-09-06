import os
import pathlib
import zipfile
from io import BytesIO

base_folder = '/friendlyfl/artifacts'

zip_prefix = '.zip'


def generate_url(run_id, task_seq, round_seq):
    if not run_id or not task_seq or not round_seq:
        return None
    return f"{base_folder}/{run_id}/{task_seq}/{round_seq}/"


def gen_zip_tmp_file(run):
    return generate_url(run.id, -1, -1)


def zip_all_files(run, url_list, file_type):
    base_url = gen_zip_tmp_file(run)
    if base_url and url_list and len(url_list) > 0:
        zip_temp_path = base_url + file_type + zip_prefix
        path = pathlib.Path(zip_temp_path)

        # Create the parent directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create the file
        path.touch()

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Add each file to the zip archive
            for file_path in url_list:
                zip_file.write(file_path, os.path.basename(file_path))

        # Seek to the beginning of the buffer
        zip_buffer.seek(0)

        # Read the content from the buffer and return it
        return zip_buffer.read()
    else:
        return None


def get_file_urls(runs, task_seq, round_seq, file_type) -> []:
    urls = []
    if not runs or len(runs) == 0 or not file_type:
        return urls
    for run in runs:
        if not run:
            continue
        saved_files = []
        if file_type == 'artifacts':
            saved_files = run.artifacts
        if file_type == 'logs':
            saved_files = run.logs
        if file_type == 'mid_artifacts':
            saved_files = run.middle_artifacts
            # if task_seq and round_seq not provided, which means users want to download all files under the run
        if task_seq and round_seq:
            prefix = generate_url(run.id, task_seq, round_seq)
            picked_files = [item for item in saved_files if prefix in item]
            urls.extend(picked_files)
        else:
            urls = saved_files
    return urls


def gen_unique_file_name(file_name, run, cur_seq, cur_round):
    return '{}-{}-{}-{}'.format(run, cur_seq, cur_round, file_name)
