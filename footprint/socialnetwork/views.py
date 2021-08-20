from django.shortcuts import render, redirect, get_object_or_404
import json

from django.http import HttpResponse, Http404
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from django.utils import timezone
# Create your views here.

from socialnetwork.forms import *
from socialnetwork.models import *
from socialnetwork.forms import ProfileForm, UpdateProfileForm
from socialnetwork.models import Profile
from allauth.account.views import SignupView, LoginView
from .models import User
import requests
from notifications.signals import notify
from notifications.models import Notification
import datetime


class MySignupView(SignupView):
    template_name = 'templates/login.html'


class MyLoginView(LoginView):
    template_name = 'templates/register.html'


@login_required
def user_profile(request):
    profile = Profile.objects.get_or_create(user=request.user)
    context = {}
    context['form'] = ProfileForm()
    context['userform'] = UpdateProfileForm()
    current_user = get_object_or_404(Profile,
                                     user=request.user)
    context['p'] = current_user
    context['following'] = current_user.following.all()
    return render(request, 'user_profile.html', context)


@login_required
# return a list of usernames
def get_following_list(user_profile):
    all_followings = user_profile.following.all()
    following_list = [following.user.username for following in all_followings]
    return following_list


@login_required
def get_photo(request, id):
    item = get_object_or_404(Profile, id=id)

    # Probably don't need this check as form validation requires a picture be uploaded.
    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)


@login_required
def get_profile(request, username):
    context = {}
    # Make sure profile is created for new users.
    _ = Profile.objects.get_or_create(user=request.user)
    request_user = get_object_or_404(Profile, user=request.user)
    profile_by_give_username = None
    try:
        profile_by_give_username = get_object_or_404(
            Profile, user__username=username)
    except:
        context["message"] = "User does not exist."
        return render(request, 'error.html', context)

    context['p'] = profile_by_give_username
    logs_of_profile = Log.objects.filter(
        user_id=profile_by_give_username.user.id)
    following_list = profile_by_give_username.following.all()
    follower_list = profile_by_give_username.follower.all()
    bookmarked_logs = profile_by_give_username.bookmarked_logs.all()
    context['following'] = following_list
    context['followers'] = follower_list
    context['bookmarked_logs'] = bookmarked_logs
    context['logs_created_by_user'] = logs_of_profile
    context['num_followers'] = len(follower_list)
    context['num_followings'] = len(following_list)
    context['num_logs'] = len(logs_of_profile)

    if request.user.username == profile_by_give_username.user.username and request.user.email == profile_by_give_username.user.email:
        return render(request, 'user_profile.html', context)

    # Post_user is not request.user, means it must be someone else's profile.
    follow_status = False
    if profile_by_give_username in request_user.following.all():
        follow_status = True
    context['following_status'] = follow_status

    return render(request, 'other_profile.html', context)


@login_required
def home(request):
    context = {}
    self_logs = Log.objects.filter(user_id=request.user.id)
    other_logs = Log.objects.exclude(user_id=request.user.id)
    self_ls = []
    for log in self_logs:
        self_geoinfo = [log.location.lat, log.location.lng,
                        log.location.placeID, str(log.picture), log.id]
        self_ls.append(self_geoinfo)
    self_ls = json.dumps(self_ls)
    context["self_geoinfo"] = self_ls
    other_ls = []
    for log in other_logs:
        if log.visibility:
            other_geoinfo = [log.location.lat, log.location.lng,
                             log.location.placeID, str(log.picture), log.id]
            other_ls.append(other_geoinfo)
    other_ls = json.dumps(other_ls)
    context["other_geoinfo"] = other_ls
    return render(request, 'home.html', context)


@login_required
def filter_date(request):
    if request.method == 'POST':
        if 'start_date' not in request.POST or 'end_date' not in request.POST:
            context = {}
            context['message'] = "Some critical data is missing! Please try again."
            return render(request, 'error.html', context)

        try:
            start_date = datetime.datetime.strptime(
                request.POST['start_date'], '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(request.POST['end_date'], '%Y-%m-%d')
            end_date = (end_date + datetime.timedelta(days=1)).date()

            if start_date > end_date:
                return render(request, 'error.html', {'message': "Start date must be earlier than end date"})
            filter_logs = Log.objects.filter(
                creation_time__range=(start_date, end_date))
        except ValueError as ve:
            return render(request, 'error.html', {'message': "ValueError"})

        return HttpResponse(serialize_log(filter_logs, request), content_type='application/json')
    else:
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})


@login_required
def filtered_stream(request):
    return render(request, 'filtered_stream.html', {})


@login_required
def get_one_log(request, log_id):
    request_log = []
    log = get_object_or_404(Log, id=log_id)
    request_log.append(log)
    return HttpResponse(serialize_log(request_log, request), content_type='application/json')


@login_required
def get_user_logs(request, user_id):
    user_logs = Log.objects.filter(user__id=user_id)
    return HttpResponse(serialize_log(user_logs, request), content_type='application/json')


@login_required
def get_logs(request):
    # Get request user's following list
    logs = Log.objects.all()
    return HttpResponse(serialize_log(logs, request), content_type='application/json')


@login_required
def get_bookmark_logs(request):
    # Get request user's following list
    request_user_profile = get_object_or_404(Profile, user=request.user)
    bookmark_list = request_user_profile.bookmarked_logs.all()
    return HttpResponse(serialize_log(bookmark_list, request), content_type='application/json')


def serialize_log(logs, request):
    request_user_profile = get_object_or_404(Profile, user=request.user)
    following_list = request_user_profile.following.all()
    bookmark_list = request_user_profile.bookmarked_logs.all()
    all_logs = []
    for log in logs:
        log_creator = log.user
        # If log creator is already followed, pass this information
        creator_profile, _ = Profile.objects.get_or_create(user=log.user)
        is_self = False
        if creator_profile == request_user_profile:
            is_self = True
        follow_status = False
        if creator_profile in following_list:
            follow_status = True
        bookmarked = False
        if log in bookmark_list:
            bookmarked = True
        liked = False
        if request_user_profile in log.liked_users.all():
            liked = True
        num_likes = len(log.liked_users.all())
        comments = []
        for comment_item in Comment.objects.all():
            if comment_item.of_log.id == log.id:
                commentor_profile = get_object_or_404(Profile, user=comment_item.created_by)
                comment = {
                    'comment_id': comment_item.id,
                    'text': comment_item.comment_content,
                    'date': comment_item.created_at.isoformat(),
                    'comment_profile_pic': str(commentor_profile.picture),
                    'username': comment_item.created_by.username,
                    'user_fn': comment_item.created_by.first_name,
                    'user_ln': comment_item.created_by.last_name,
                }
                comments.append(comment)
        log_info = {
            'user_id': log_creator.id,
            'already_followed': follow_status,
            'log_id': log.id,
            'username': log_creator.username,
            'profile_pic': str(creator_profile.picture),
            'log_title': log.log_title,
            'log_text': log.log_text,
            'log_location': log.location.location_name,
            'date': log.creation_time.isoformat(),
            'log_pic': str(log.picture),
            'bookmark_status': bookmarked,
            'num_likes': num_likes,
            'already_liked': liked,
            'comments': comments,
            'is_self': is_self,
            'visibility': log.visibility
        }
        all_logs.append(log_info)
    response_json = json.dumps(all_logs)
    return response_json


@login_required
def add_profile(request):
    context = {}
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    user_form = UpdateProfileForm(request.POST)
    if not user_form.is_valid():
        if 'first_name' in request.POST and request.POST['first_name']:
            request.user.first_name = request.POST['first_name']
        if 'last_name' in request.POST and request.POST['last_name']:
            request.user.last_name = request.POST['last_name']
        if 'username' in request.POST and request.POST['username']:
            num_users_with_username = User.objects.filter(username=request.POST['username']).count()
            if num_users_with_username > 0 and request.POST['username'] != request.user.username:
                context['message'] = 'Username already exists.'
            return render(request, 'error.html', context)
            request.user.username = request.POST['username']
        request.user.save()
    else:
        request.user.first_name = request.POST['first_name']
        request.user.last_name = request.POST['last_name']
        num_users_with_username = User.objects.filter(username=request.POST['username']).count()
        if num_users_with_username > 0 and request.POST['username'] != request.user.username:
            context['message'] = 'Username already exists.'
            return render(request, 'error.html', context)
        request.user.username = request.POST['username']
        request.user.save()

    new_item = Profile.objects.get(user=request.user)
    form = ProfileForm(request.POST, request.FILES, instance=new_item)
    if not form.is_valid():  # 检查两个field
        # context['form'] = form
        if 'bio' in request.POST and request.POST['bio']:
            new_item.bio = request.POST['bio']
        if 'picture' in form.cleaned_data:
            new_item.picture = form.cleaned_data['picture']
            new_item.content_type = form.cleaned_data['picture'].content_type
        # else:
        #     context["message"] = "Image setting failed. You must upload an image."
        #     return render(request, 'error.html', context)
        new_item.save()
        context['p'] = new_item
        return get_profile(request, request.user.username)
    else:
        # Must copy content_type into a new model field because the model
        # FileField will not store this in the database.  (The uploaded file
        # is actually a different object than what's return from a DB read.)
        new_item.pic = form.cleaned_data['picture']
        new_item.bio = form.cleaned_data['bio']
        new_item.content_type = form.cleaned_data['picture'].content_type
        new_item.save()

        context['message'] = 'Item #{0} saved.'.format(new_item.id)
        context['p'] = new_item
    return get_profile(request, request.user.username)


@login_required
def follow(request, id):
    context = {}
    other_user = None
    try:
        other_user = get_object_or_404(Profile, id=id)
    except:
        context["message"] = "The user profile you are trying to follow doesn't exist."
        return render(request, 'error.html', context)
    current_user = request.user
    # Other user is a profile
    current_user.profile.following.add(other_user)
    current_user.save()
    other_user.follower.add(current_user.profile)
    other_user.save()

    context['following_status'] = True
    context['p'] = other_user

    return get_profile(request, other_user.user.username)


@login_required
def ajax_follow(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    if not 'user_id' in request.POST or not request.POST['user_id']:
        return render(request, 'error.html', {'message': "The user you are trying to follow should not have empty ID."})

    user_id = request.POST['user_id']
    if user_id.isnumeric():
        other_user_profile = get_object_or_404(Profile, user_id=user_id)
        request_user_profile = get_object_or_404(Profile, user=request.user)
        # Sanity check, users can't follow themselves
        if request_user_profile != other_user_profile:
            # Only Return when request_user_profile doesn't include the profile trying to follow.
            if other_user_profile not in request_user_profile.following.all():
                request_user_profile.following.add(other_user_profile)
                request_user_profile.save()
                other_user_profile.follower.add(request_user_profile)
                other_user_profile.save()
            else:
                return get_logs(request)

    return get_logs(request)


@login_required
def ajax_unfollow(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    if not 'user_id' in request.POST or not request.POST['user_id']:
        return render(request, 'error.html', {'message': "The user you are trying to follow should not have empty ID."})

    user_id = request.POST['user_id']
    if user_id.isnumeric():
        other_user_profile = get_object_or_404(Profile, user_id=user_id)
        request_user_profile = get_object_or_404(Profile, user=request.user)
        # Sanity check, users can't follow themselves
        if request_user_profile != other_user_profile:
            # Only Return when request_user_profile doesn't include the profile trying to follow.
            if other_user_profile in request_user_profile.following.all():
                request_user_profile.following.remove(other_user_profile)
                request_user_profile.save()
                other_user_profile.follower.remove(request_user_profile)
                other_user_profile.save()

    return get_logs(request)


@login_required
def unfollow(request, id):
    context = {}
    other_user = None
    try:
        other_user = get_object_or_404(Profile, id=id)
    except:
        context["message"] = "The user profile you are trying to unfollow doesn't exist."
        return render(request, 'error.html', context)

    current_user = request.user
    current_user.profile.following.remove(other_user)
    current_user.save()

    other_user.follower.remove(current_user.profile)
    other_user.save()
    context['following_status'] = False
    context['p'] = other_user

    return get_profile(request, other_user.user.username)


@login_required
def add_comment(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    if not 'comment_text' in request.POST or not request.POST['comment_text']:
        return render(request, 'error.html', {'message': "You comment should not be empty."})

    if not 'log_id' in request.POST or not request.POST['log_id']:
        return render(request, 'error.html', {'message': "Comment needs to be made on a log."})

    logid = request.POST['log_id']
    if logid.isnumeric():
        belong_to_log = Log.objects.get(id=logid)
        new_comment = Comment(comment_content=request.POST['comment_text'],
                              created_by=request.user,
                              created_at=timezone.now(),
                              of_log=belong_to_log)
        new_comment.save()
        notify.send(sender=request.user, recipient=belong_to_log.user,
                    verb='your log: <i>{}</i> has a new reply from <strong>{}</strong>: "{}"'.format(
                        belong_to_log.log_title,
                        new_comment.created_by.username,
                        new_comment.comment_content),
                    description="Comment",
                    target=belong_to_log)
        return get_logs(request)
    elif logid == 'xxxx':
        return render(request, 'error.html', {'message': "Please dont' make changes to comment field name"})


@login_required
def log_editor(request):
    context = {}
    if request.method == 'POST':
        if 'latLng' not in request.POST or not request.POST['latLng']:
            context['message'] = "Some critical data is missing! Please try again."
            return render(request, 'error.html', context)
        try:
            latLng = json.loads(request.POST['latLng'])
        except:
            context['message'] = "Some critical data is missing! Please try again."
            return render(request, 'error.html', context)

        if 'lat' not in latLng or 'lng' not in latLng:
            context['message'] = "Some critical data is missing! Please try again."
            return render(request, 'error.html', context)

        try:
            float(latLng['lat'])
            float(latLng['lng'])
        except ValueError:
            context['message'] = "Some critical data is wrong! Please try again."
            return render(request, 'error.html', context)

        try:
            location = Location.objects.get(lat=float(latLng['lat']), lng=float(latLng['lng']))
            context['location_name'] = location.location_name
            context['placeID'] = location.placeID
        except Location.DoesNotExist:
            if 'location_name' in request.POST and 'placeID' in request.POST:
                context['location_name'] = request.POST['location_name']
                context['placeID'] = request.POST['placeID']
            else:
                context['location_name'] = getLocationNameFromLatLng(latLng)
                context['placeID'] = str(latLng['lat']) + str(latLng['lng'])

            location = Location(
                placeID=context['placeID'],
                location_name=context['location_name'],
                lat=float(latLng['lat']),
                lng=float(latLng['lng']))
            location.save()

        context['log_id'] = 0
        context['log_title'] = ''
        context['log_text'] = ''
        context['visibility'] = True

        logs = Log.objects.filter(location=location)
        context['log_num'] = len(logs)
        user_set = set()
        for log in logs:
            user_set.add(log.user)
        context['user_num'] = len(user_set)

        return render(request, 'log_editor.html', context)
    else:
        context['message'] = "The page you try to visit only accepts POST request."
        return render(request, 'error.html', context)


@login_required
def edit_log(request, log_id):
    context = {}
    log = get_object_or_404(Log, id=log_id)
    if log.user != request.user:
        context['message'] = "You cannot edit other user's log."
        return render(request, 'error.html', context)
    context['log_id'] = log.id
    context['log_title'] = log.log_title
    context['log_text'] = log.log_text
    context['visibility'] = log.visibility
    context['placeID'] = log.location.placeID
    context['location_name'] = log.location.location_name
    logs = Log.objects.filter(location=log.location)
    context['log_num'] = len(logs)
    user_set = set()
    for log in logs:
        user_set.add(log.user)
    context['user_num'] = len(user_set)
    return render(request, 'log_editor.html', context)


@login_required
def add_log(request, log_id):
    context = {}
    if request.method == 'POST':
        form = EditorForm(request.POST, request.FILES)
        try:
            location = Location.objects.get(placeID=request.POST['placeID'])
        except Location.DoesNotExist:
            location = None

        if not location:
            context['message'] = 'Location not found.'
            return render(request, 'error.html', context)

        try:
            log = Log.objects.get(id=log_id)
            if log.user.id != request.user.id:
                context['message'] = "You cannot edit other user's log."
                return render(request, 'error.html', context)
        except Log.DoesNotExist:
            log = None

        if not form.is_valid():
            error_messages = []
            if 'log_title' in request.POST and len(request.POST['log_title']) > 200:
                error_messages.append("Log title exceeds max length (200).")
            if 'log_text' in request.POST and len(request.POST['log_text']) > 20000000:
                error_messages.append("Log text exceeds max length (20000).")
            if 'picture' not in form.cleaned_data and 'picture' in request.FILES:
                if not hasattr(request.FILES['picture'], 'content_type'):
                    error_messages.append('You must upload a picture.')
                elif not request.FILES['picture'].content_type or not request.FILES['picture'].content_type.startswith(
                        'image'):
                    error_messages.append('File type is not image.')
                elif request.FILES['picture'].size > 2500000:
                    error_messages.append('Cover image exceeds max size (2500000).')
            context['log_id'] = log_id
            if 'log_title' in request.POST:
                context['log_title'] = request.POST['log_title']
            else:
                context['log_title'] = ''

            if 'log_text' in request.POST:
                context['log_text'] = request.POST['log_text']
            else:
                context['log_text'] = ''

            if 'visibility' in request.POST:
                context['visibility'] = False
            else:
                context['visibility'] = True
            context['placeID'] = form.cleaned_data['placeID']
            context['location_name'] = location.location_name
            context['error_messages'] = error_messages
            return render(request, 'log_editor.html', context)

        try:
            log = Log.objects.get(id=log_id)
            log.log_title = form.cleaned_data['log_title']
            log.log_text = form.cleaned_data['log_text']
            if form.cleaned_data['picture']:
                log.picture = form.cleaned_data['picture']
                log.content_type = form.cleaned_data['picture'].content_type
            if 'visibility' in request.POST:
                log.visibility = False
            else:
                log.visibility = True
            log.save()
        except Log.DoesNotExist:
            new_log = Log(log_title=form.cleaned_data['log_title'],
                          log_text=form.cleaned_data['log_text'],
                          user=request.user,
                          location=location)
            if form.cleaned_data['picture']:
                new_log.picture = form.cleaned_data['picture']
                new_log.content_type = form.cleaned_data['picture'].content_type
            if 'visibility' in request.POST:
                new_log.visibility = False
            else:
                new_log.visibility = True
            new_log.save()
        return redirect(reverse('home'))
    else:
        context['message'] = "The page you try to visit only accepts POST request."
        return render(request, 'error.html', context)


@login_required
def get_picture(request, log_id):
    log = get_object_or_404(Log, id=log_id)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not log.picture:
        raise Http404

    return HttpResponse(log.picture, content_type=log.content_type)


@login_required
def log_display(request):
    if request.method == 'POST':
        context = {}
        if 'latLng' not in request.POST or not request.POST['latLng']:
            context['message'] = "Some critical data is missing! Please try again."
            return render(request, 'error.html', context)

        try:
            latLng = json.loads(request.POST['latLng'])
        except:
            context['message'] = "Some critical data is missing! Please try again."
            return render(request, 'error.html', context)

        if 'lat' not in latLng or 'lng' not in latLng:
            context['message'] = "Some critical data is missing! Please try again."
            return render(request, 'error.html', context)

        try:
            float(latLng['lat'])
            float(latLng['lng'])
        except ValueError:
            context['message'] = "Some critical data is wrong! Please try again."
            return render(request, 'error.html', context)

        latLng = json.loads(request.POST['latLng'])
        location = Location.objects.filter(
            lat=float(latLng['lat']), lng=float(latLng['lng']))[0]
        logs_to_display = list(Log.objects.filter(location=location, visibility=True))
        logs_to_display.extend(Log.objects.filter(location=location, user=request.user, visibility=False))
        context['logs'] = logs_to_display
        logs = Log.objects.filter(location=location)
        context['log_num'] = len(logs)
        user_set = set()
        for log in logs:
            user_set.add(log.user)
        context['user_num'] = len(user_set)

        return render(request, 'log_display.html', context)
    else:
        context = {}
        context['message'] = "The page you try to visit only accepts POST request."
        return render(request, 'error.html', context)


def getLocationNameFromLatLng(latLng):
    # detailed retured json information please visit: https: // maps.googleapis.com/maps/api/geocode/json?latlng = 40.714224, -73.961452 & key = AIzaSyBAzuMuqCtP0j8Yd7hJ6CG5jdei-Y4Pdlw
    URL = "https://maps.googleapis.com/maps/api/geocode/json"
    lat = latLng['lat']
    lng = latLng['lng']
    latLng_ = "{},{}".format(lat, lng)
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'latlng': latLng_,
              'key': 'AIzaSyBAzuMuqCtP0j8Yd7hJ6CG5jdei-Y4Pdlw'
              }

    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS)

    # extracting data in json format
    data = r.json()

    # extracting latitude, longitude and formatted address
    # of the first matching location(the nearest location to the given latlng)
    latitude = data['results'][0]['geometry']['location']['lat']
    longitude = data['results'][0]['geometry']['location']['lng']
    formatted_address = data['results'][0]['formatted_address']

    # # printing the output
    return formatted_address


@login_required
def travel_stream(request):
    # make sure user profile is created before accessing stream page.
    # make sure user profile is created before accessing stream page.
    request_user = Profile.objects.get_or_create(user=request.user)
    return render(request, 'travel_stream.html', {})


@login_required
def bookmark_stream(request):
    # make sure user profile is created before accessing stream page.
    request_user = Profile.objects.get_or_create(user=request.user)
    return render(request, 'bookmark_stream.html', {})


@login_required
def show_all_user_stream(request, user_id):
    # make sure user profile is created before accessing stream page.
    request_user = Profile.objects.get_or_create(user=request.user)
    return render(request, 'user_stream.html', {'user_id': user_id})


@login_required
def one_log(request, log_id):
    try:
        valid_log = get_object_or_404(Log, id=log_id)
    except:
        context = {}
        context["message"] = "The log you are trying to display doesn't exist"
        return render(request, 'error.html', context)
    return render(request, 'one_log.html', {'log_id': log_id})


@login_required
def my_notifications(request):
    context = {}
    return render(request, 'my_notifications.html', context)


# Add this log to User's bookmarked collection
@login_required
def add_bookmark(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    if not 'log_id' in request.POST or not request.POST['log_id']:
        return render(request, 'error.html', {'message': "The log you are trying to bookmark shall not be empty."})

    logid = request.POST['log_id']
    if logid.isnumeric():
        log_trying_to_bookmark = Log.objects.get(id=logid)
        request_user = get_object_or_404(Profile, user=request.user)
        request_user_current_collection = request_user.bookmarked_logs
        if log_trying_to_bookmark in request_user_current_collection.all():
            return render(request, 'error.html', {'message': "Log is already bookmarked, please check your collection"})
        else:
            request_user.bookmarked_logs.add(log_trying_to_bookmark)
            request_user.save()

        return get_logs(request)
    elif logid == 'xxxx':
        return render(request, 'error.html', {'message': "Please dont' make changes to comment field name"})


# Remove this log from User's bookmarked collection
@login_required
def remove_bookmark(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    if not 'log_id' in request.POST or not request.POST['log_id']:
        return render(request, 'error.html', {'message': "The log you are trying to bookmark shall not be empty."})

    logid = request.POST['log_id']
    if logid.isnumeric():
        log_trying_to_remove = Log.objects.get(id=logid)
        request_user = get_object_or_404(Profile, user=request.user)
        request_user_current_collection = request_user.bookmarked_logs
        if log_trying_to_remove not in request_user_current_collection.all():
            return render(request, 'error.html', {'message': "You can not remove a collection that is not bookmarked."})
        else:
            request_user.bookmarked_logs.remove(log_trying_to_remove)
            request_user.save()

        return get_logs(request)
    else:
        return render(request, 'error.html', {'message':
                                                  "Please dont' make changes to comment field name"})


# Like this log, add liked users to this log
@login_required
def like_log(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    if not 'log_id' in request.POST or not request.POST['log_id']:
        return render(request, 'error.html', {'message': "The log you are trying to like shall not be empty."})

    logid = request.POST['log_id']
    if logid.isnumeric():
        log_trying_to_like = Log.objects.get(id=logid)
        request_user = get_object_or_404(Profile, user=request.user)
        logs_liked_users = log_trying_to_like.liked_users
        if request_user in logs_liked_users.all():
            return render(request, 'error.html', {'message': "You already liked this Log"})
        else:
            logs_liked_users.add(request_user)
            log_trying_to_like.save()

            notify.send(sender=request.user, recipient=log_trying_to_like.user,
                        verb='Wow! Your log: <i>{}</i> is liked by <strong>{}</strong>.'.format(
                            log_trying_to_like.log_title,
                            request.user.username),
                        description="Like",
                        target=log_trying_to_like)

        return get_logs(request)
    elif logid == 'xxxx':
        # print(postid.isnumeric())
        return render(request, 'error.html', {'message':
                                                  "Please dont' make changes to comment field name"})


# Unlike this log, remove request user from liked_users of this Log
# Like this log, add liked users to this log
@login_required
def unlike_log(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})

    if not 'log_id' in request.POST or not request.POST['log_id']:
        return render(request, 'error.html', {'message': "The log you are trying to like shall not be empty."})

    logid = request.POST['log_id']
    if logid.isnumeric():
        log_trying_to_unlike = Log.objects.get(id=logid)
        request_user = get_object_or_404(Profile, user=request.user)
        if request_user not in log_trying_to_unlike.liked_users.all():
            return render(request, 'error.html', {'message':
                                                      "You can't unlike this Log since it's not liked."})
        else:
            log_trying_to_unlike.liked_users.remove(request_user)
            log_trying_to_unlike.save()

        return get_logs(request)
    elif logid == 'xxxx':
        return render(request, 'error.html', {'message':
                                                  "Please dont' make changes to comment field name"})


@login_required
def mark_as_read_action(request):
    if request.method == 'POST':
        if 'notification_id' not in request.POST or not request.POST['notification_id'] or 'log_id' not in request.POST or not request.POST['log_id']:
            return render(request, 'error.html', {'message': "Some critical data is missing. Please try again!"})
        notification_id = request.POST['notification_id']
        try:
            log_id = int(request.POST['log_id'])
        except ValueError:
            return render(request, 'error.html', {'message': "Some critical data is wrong. Please try again!"})
        notification = get_object_or_404(Notification, id=notification_id)
        if notification.unread:
            notification.unread = False
            notification.save()
        return redirect(reverse('one_log', kwargs={'log_id': log_id}))
    else:
        return render(request, 'error.html', {'message': "You must use a POST request for this operation"})


@login_required
def about(request):
    return render(request, 'about.html', {})