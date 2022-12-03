from django.shortcuts import render,redirect
from webscraperapp.Main import main
# from webscraperapp.Main import progress
import os
import mimetypes
from django.http.response import HttpResponse
from django.contrib.auth import login, authenticate,logout
from django.views.decorators.csrf import csrf_protect
flag = False
filename1 = None

@csrf_protect
def home(request):
    latest_first = os.listdir(os.getcwd() + '/outputfiles')
    latest_first.reverse()
    csvfiles= {"filename":latest_first}
    global flag
    if request.user.is_authenticated:
        if request.method == 'GET':
            if flag:
                print("Scraper is still scraping lst data")
                from webscraperapp.Main import progress
                context = {"message": f"Scraper is still scraping previously uploaded data", "flag": flag,"csvfiles":csvfiles,"progress":round(progress,2)}
                return render(request, 'home.html',context=context)
            url=request.POST.get('url')
            print(url)
            return render(request, 'home.html',context={"csvfiles":csvfiles})
        if request.method == 'POST':
            if flag:
                print("Scraper is still scraping lst dataaaaaaa")      
                context = {"message": "Scraper is still scraping lst dataaaaaaaa", "flag": flag,"csvfiles":csvfiles}
                return render(request, 'home.html',context=context)
            else:
                names = request.POST.get('names').split(',')
                locations = request.POST.get('locations').split('\n')
                for loc in locations:
                    if loc == '':
                        locations.remove(loc)
                print(locations)
                url=request.POST.get('url')
                print(url)
                flag = True
                filename = main(names, locations)
                file = os.path.join(os.getcwd(), f'{filename}')
                context = {"message": "Scraping Done", "flag": flag,"filename":file,"csvfiles":csvfiles}
                flag = False
                return render(request, 'home.html',context=context)        
    else:
        return redirect('login')

@csrf_protect
def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        # check iff user credentials are correct
        user = authenticate(username=username, password=password)
        if user is not None:
            # Backend authenticated the credentials
            login(request,user)
            print("User is logged in")
            return redirect('home')
        else:
            # Backend did not authenticated the credentials
            print("User is not logged in")
            return redirect('login')
    if request.method == 'GET':
        return render(request, 'login.html')

def progress(request):
    if request.method == 'POST':
        from webscraperapp.Main import progress
        return HttpResponse(progress)

def logoutUser(request):
    logout(request)
    return redirect('login')
  
def download_file(request,filename1):
    if request.method == 'GET':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(BASE_DIR)
        filename = filename1
        filepath = BASE_DIR + '/outputfiles/' + filename
        path = open(filepath, 'r')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        print('filedownload started',filepath)
        return response

def backup_names(request):
    if request.method == 'GET':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backupfiles_loc = BASE_DIR + "/backup"
        files = os.listdir(backupfiles_loc)
        backupname_path = backupfiles_loc + "/" + files[1]
        # backuplocation_path = backupfiles_loc + "/" + files[0]
        path = open(backupname_path, 'r')
        mime_type, _ = mimetypes.guess_type(backupname_path)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" %files[1]
        return response

def backup_locations(request):
    if request.method == 'GET':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backupfiles_loc = BASE_DIR + "/backup"
        files = os.listdir(backupfiles_loc)
        backupname_path = backupfiles_loc + "/" + files[0]
        # backuplocation_path = backupfiles_loc + "/" + files[0]
        path = open(backupname_path, 'r')
        mime_type, _ = mimetypes.guess_type(backupname_path)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" %files[0]
        return response