from django import forms
from django.forms import MultiWidget, TextInput
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from socialnetwork.models import *
from socialnetwork.models import Profile

MAX_UPLOAD_SIZE = 2500000


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name',
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name',
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        profile = Profile.objects.create(user=user)
        profile.save()


class FilterForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        if 'start_date' in cleaned_data.keys() & 'end_date' in cleaned_data.keys():
            start_date = clean_data.get('start_date')
            end_date = clean_data.get('end_date')
            if start_date > end_date:
                raise forms.ValidationError("Start date later than end date")
        else:
            raise forms.ValidationError("A start date and end date are required")
        return cleaned_data


class UpdateProfileForm(forms.Form):
    username = forms.CharField(required=True)
    first_name = forms.CharField(max_length=30, label='First Name',
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name',
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

    # def save(self, commit=True):
    #     user = super(SignupForm, self).save(commit=False)
    #     if commit:
    #         user.save()


class EditorForm(forms.Form):
    log_title = forms.CharField(max_length=200)
    log_text = forms.CharField(required=False, max_length=20000000)
    placeID = forms.CharField(required=False)
    picture = forms.FileField(required=False)

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture:
            return picture
        if picture and not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture


class EntryForm(forms.Form):
    last_name = forms.CharField(max_length=20)
    first_name = forms.CharField(max_length=20)
    birthday = forms.DateField(required=False)
    children = forms.IntegerField(required=False, label='# of children')
    address = forms.CharField(required=False, max_length=200)
    city = forms.CharField(required=False, max_length=30)
    state = forms.CharField(required=False, max_length=20)
    zip_code = forms.CharField(required=False, max_length=10)
    country = forms.CharField(required=False, max_length=30)
    email = forms.CharField(required=False, max_length=32)
    phone_number = forms.CharField(required=False, max_length=16, label='Phone #')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200, widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=200,
                                label='Password',
                                widget=forms.PasswordInput(attrs={'id': 'id_password', }))
    password2 = forms.CharField(max_length=200,
                                label='Confirm',
                                widget=forms.PasswordInput(attrs={'id': 'id_confirm_password', }))
    email = forms.CharField(max_length=50,
                            label='E-mail',
                            )  # widget = forms.EmailInput()
    first_name = forms.CharField(max_length=20,
                                 label='First Name')
    last_name = forms.CharField(max_length=20,
                                label='Last Name')

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


MAX_UPLOAD_SIZE = 2500000


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'picture')

    # class Meta:
    #     model = User
    #     fields = ('username','first_name', 'last_name')

    # def clean_bio(self):
    #     bio = self.cleaned_data.get('bio')
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture
