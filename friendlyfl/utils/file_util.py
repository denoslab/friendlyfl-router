import os
import zipfile

base_folder = '/friendlyfl/artifacts'

artifact_file = '/artifacts.zip'


def generate_artifacts_url(project_id, batch, participant_id):
    if not project_id or not batch or not participant_id:
        return None
    return f"{base_folder}/{project_id}/{batch}/{participant_id}"
