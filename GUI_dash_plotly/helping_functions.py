import os
import datetime   


def find_data_in_folder(folder_path: str):
    """ Find the data in the folder and the creation time of the files.
    :param folder_path: The path to the folder
    :type folder_path: str
    :return: The data in the folder and the creation time of the files
    :rtype: str, bool
    return: Boolean, if a message is returned and therefore a popup should be shown
    :rtype: bool
    """
    if not os.path.exists(folder_path):
        print("The folder does not exist.")
        return "The folder does not exist.", True

    files = os.listdir(folder_path)
    if not files:
        print("No files found in the folder.")
        return "No files found in the folder.", True
    file_info = []
    for file in files:
        file_path = os.path.join(folder_path, file)
        last_change_time = os.path.getmtime(file_path)
        last_change_time_str = datetime.datetime.fromtimestamp(last_change_time).strftime('%Y-%m-%d %H:%M:%S')
        # creation_time = os.path.getctime(file_path)
        # creation_time_str = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
        file_info.append(f"{file}: {last_change_time_str}")
    return "\n".join(file_info), True