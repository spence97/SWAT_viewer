from tethys_sdk.services import get_spatial_dataset_engine
import os
from shutil import copyfile
from .app import swat as app
from .config import temp_workspace, data_path

WORKSPACE = 'swat'
GEOSERVER_URI = 'http://www.example.com/swat'

def save_files(id):

    rch_path = os.path.join(data_path, id)
    temp_path = temp_workspace
    temp_files = os.listdir(temp_path)

    for file in temp_files:
        if file.endswith('.rch'):
            print('saving file to app workspace')
            temp_file_path = os.path.join(temp_path, file)
            perm_file_path = os.path.join(rch_path, file)
            copyfile(temp_file_path, perm_file_path)
            os.remove(temp_file_path)
        elif file.endswith('.zip'):
            print('uploading file to geoserver')
            temp_file_path = os.path.join(temp_path, file)
            '''
            Check to see if shapefile is on geoserver. If not, upload it.
            '''
            geoserver_engine = get_spatial_dataset_engine(name='byu')
            response = geoserver_engine.get_layer(file, debug=True)
            if response['success'] == False:

                #Create the workspace if it does not already exist
                response = geoserver_engine.list_workspaces()
                if response['success']:
                    workspaces = response['result']
                    if WORKSPACE not in workspaces:
                        geoserver_engine.create_workspace(workspace_id=WORKSPACE, uri=GEOSERVER_URI)

                #Create a string with the path to the zip archive
                zip_archive = temp_file_path

                # Upload shapefile to the workspaces
                if 'reach' in file or 'drainageline' in file or 'stream' in file or 'river' in file:
                    store = id + '-reach'
                elif 'subbasin' in file or 'catch' in file or 'boundary' in file:
                    store = id + '-subbasin'
                print(store)
                store_id = WORKSPACE + ':' + store
                print(store_id)
                geoserver_engine.create_shapefile_resource(
                    store_id=store_id,
                    shapefile_zip=zip_archive,
                    overwrite=True
                )
            os.remove(temp_file_path)