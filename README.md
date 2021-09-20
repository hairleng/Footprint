## Demo website (server has been closed)

https://cmu-footprint.com

http://cmu-footprint.com

## Main pages

- Register/Login django auth + Oauth 
- Home/Map Page(show 'footprint' of everyone or just me on the world map (google api)
- Log Display & Edit page
- World Page (support filter by date, like, add to favorite, comment)
- Bookmark Page (display logs in my bookmark)
- Live Notification
- Personal Information


## Dependencies

see requirements.txt

## Cloud Update Pipeline

```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic

sudo chgrp -R www-data footprint
chmod -R g+w footprint
sudo apache2ctl restart
```
