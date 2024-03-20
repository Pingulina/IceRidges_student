# return the mooring locations (lat and lon) for the measurements
import os
import json

def mooring_locations(storage_path = None):
    """Return the mooring locations (lat and lon) for the measurements for all measured years
    :param storage_path: (optional), str, path to the folder where the mooring_locations.json file should be stored
    :return: dictionary with the mooring locations
    :rtype: dict
    """
    # if the file mooring_locations.json already exists, return the mooring_dict
    if storage_path is not None:
        file_storage = os.path.join(storage_path, 'mooring_locations.json')
        if os.path.exists(file_storage):
            use_existing = input(f"The file {file_storage} already exists. Do you want to use the existing file (Y/y) or create a new one (N/n)?")
            if use_existing == 'Y' or use_existing == 'y':
                with open(file_storage, 'r') as file:
                    mooring_dict = json.load(file)
                print(f"Mooring locations loaded from {file_storage}")
                return mooring_dict
        
    path_name = r"C:\Users\cls8575\Documents\NTNU\IceRidges-main\Data_Beaufort_Gyre_Exploration_Project"
    mooring_dict = {}
    for folder in os.listdir(path_name):
        file_path = os.path.join(path_name, folder, 'dat_files')
        # for all files in file_path ending with .dat
        for file in os.listdir(file_path):
            if file.endswith('.dat'):
                # open the file and read the lines
                with open(os.path.join(file_path, file), 'r') as file_dat:
                    data = file_dat.readlines()
                # the first line is: %BG yyyy-yyyy Mooring {a, b, c, d} lat lon
                # get lat and lon from the first line
                meta_data = data[0].split(':')[0].split()
                mooring_year = meta_data[1] # get the year
                mooring_pos = meta_data[-1].lower() # get the mooring position (.lower() to make it lower case)
                pos = (data[0].split(':')[-1].split(','))
                lat = pos[0].split()
                lon = pos[1].split()
                lat = dm2d(int(lat[0]), float(lat[1]), lat[2])
                lon = dm2d(int(lon[0]), float(lon[1]), lon[2])
                # store the lat and lon in the mooring_dict
            
                if mooring_year in mooring_dict:
                    mooring_dict[mooring_year][mooring_pos] = {'lat': lat, 'lon': lon}
                else:
                    mooring_dict[mooring_year] = {mooring_pos: {'lat': lat, 'lon': lon}}

    if storage_path is not None:
        # store the mooring_dict in a .json file
        file_storage = os.path.join(storage_path, 'mooring_locations.json')
        # if the storage path does not exist, create it
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        with open(file_storage, 'w') as file:
            json.dump(mooring_dict, file)
        print(f"Mooring locations stored in {file_storage}")            
    return mooring_dict

def dm2d(degrees:int, minutes:float, compass:str):
    """Convert degrees and minutes to degrees
    :param degrees: degrees
    :type degrees: int
    :param minutes: minutes
    :type minutes: float
    :return: degrees
    :rtype: float
    """
    if compass == 'N' or compass == 'E':
        return degrees + minutes/60
    elif compass == 'S' or compass == 'W':
        return -(degrees + minutes/60)
    else:
        return None

if __name__ == "__main__":
    print(mooring_locations())
    print('Done!')

