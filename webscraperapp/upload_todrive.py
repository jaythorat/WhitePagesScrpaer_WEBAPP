# Importing necessary modules
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


gauth = GoogleAuth()      
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)  

# creating a function to upload a file to google drive
def upload_file(upload_file_list):
    for upload_file in upload_file_list:
        gfile = drive.CreateFile({'title': upload_file})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(upload_file)
        gfile.Upload() # Upload the file.
        return gfile

# Calling the function to upload the file
if __name__ == '__main__':
    upload_file_list = ['main.py']
    upload_file(upload_file_list)