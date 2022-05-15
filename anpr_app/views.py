from django.contrib.auth.mixins import LoginRequiredMixin
from anpr_app.models import Photo, User, VehicleOwner
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .anpr import license_plate_recognition
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from pathlib import Path
from PIL import Image
import json, os


BASE_DIR = Path(__file__).resolve().parent.parent


class DashBoardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"Gender": ['Male','Female']})
        return context

	
class RegistrationTempView(TemplateView):
    template_name='sign_up.html'
   
    def post(self, request):
        if request.method == 'POST':
            email = request.POST['email'].lower()
            first_name = request.POST['first_name'].title()
            last_name = request.POST['last_name'].title()
            gender = request.POST['gender']
            contact = request.POST['contact']
            password = request.POST['password']
            compsd = request.POST['compsd']  
            queryset = User.objects.filter(email__iexact=email)
            if not queryset.exists():
                if password == compsd and len(password) >= 8:
                    user = User.objects.create_user(
                        email = email,
                        first_name = first_name,
                        last_name = last_name,
                        gender = gender,
                        contact = contact
                    )
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'Registered Successfully!')  
                else:
                    messages.error(request, 'Invalid Password!')
            else:
                messages.error(request, f'Sorry {email} already exist!')
        return render(request, 'sign_up.html')


class LoginTempView(TemplateView):
    template_name='sign_in.html'
    
    def post(self, request):
        if request.method == 'POST':
            email = request.POST['email'].lower()
            password = request.POST['password']
            queryset = User.objects.filter(email__iexact=email)
            user = None
            try:
                user = User.objects.get(email__exact=email)
            except User.DoesNotExist:
                messages.error(request, f'Sorry {email} doesn\'t exist!') 
            if queryset.exists():                
                if user.check_password(password):                    
                    login(request, user)
                    messages.success(request, 'Login Successfully!')
                    return redirect('recognize:dashboard')
                else:
                    messages.error(request, 'Invalid Password!')
        return render(request, 'sign_in.html')


def logout_request(request):
	logout(request)
	return redirect("home")


def plate_number_processed(request):
    if request.method == 'POST':
        file = request.FILES.get('myfile', False)
        if file:
            file_name = file.name
            img_path = os.path.join(settings.BASE_DIR, f'media/plate_num_uploads/{file_name}')
            img = Image.open(file)
            img.save(img_path)
            
            licease_num, save_thresh = license_plate_recognition(img_path)

            thresh_path = os.path.join(settings.BASE_DIR, save_thresh)                          
            img_ = Image.open(thresh_path).filename            
            imgFile = Photo(img=img_)            
                            
            queryshot = VehicleOwner.objects.filter(plate_number__exact=licease_num)
            if queryshot.exists():                    
                return HttpResponse(json.dumps({
                    "status": "true", 
                    'plate': licease_num, 
                    'name': f'{queryshot.first().first_name} {queryshot.first().last_name}',
                    'age': queryshot.first().age,
                    'model': queryshot.first().vehicle_model,
                    'date': str(datetime.now().strftime("%d-%m-%Y %H:%M")),
                    'url': queryshot.first().avatar.url, 
                    'imgurl': imgFile.img.url,
                    # 'roiurl': imgFile_roi.roi.url,               
                }))
            else:
                return HttpResponse(json.dumps({
                    'status': 'false',
                    'plate': licease_num,
                    'imgurl': imgFile.img.url,
                    'messsage': f'Sorry {licease_num} does not exist!',
                }))           
            
        else:
            messages.error(request, 'Upload an Image!')