from shareplum.office365 import Office365
from shareplum.site import Site
from shareplum.site import Version
import os

if __name__ == '__main__':
    file_path = fr'{os.getenv("FILEPATH")}'
    file_name = os.getenv('FILENAME')
    sp_url = os.getenv('SP_URL')
    sp_username = os.getenv('SP_USERNAME')
    sp_password = os.getenv('SP_PASSWORD')
    sp_site = os.getenv('SP_SITE')
    sp_folder = os.getenv('SP_FOLDER')
    with open(file_path, mode='rb') as file:
        content = file.read()
    cookie = Office365(share_point_site=sp_url, username=sp_username, password=sp_password).GetCookies()
    site = Site(f'{sp_url}{sp_site}', version=Version.v365, authcookie=cookie)
    folder = site.Folder(sp_folder)
    folder.timeout = 30
    folder.upload_file(content, file_name)
