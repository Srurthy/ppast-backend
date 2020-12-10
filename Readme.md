# PPAST

## Don't try to run. Just a sample code

## Run PPAST
  - OS: Any Debian derivatives
  - setup dependencies
    - `sudo apt intall docker.io`
    - `sudo usermod -aG docker $USER` if you want to use docker without sudo
  - build docker image
    - `cd path/to/ppast-backend`
    - `docker build -t ppast .`
    - NOTE: you need to rebuild the container to reflect the code changes.
  - create superuser if needed
    - `docker run -p 8000:8000 -i -t ppast pipenv run ./manage.py createsuperuser`
  - run it
    - `docker run -p 8000:8000 -i -t ppast`

## create role and database
    sudo su - postgres
    createuser --interactive --pwprompt
    createdb -O ppast ppast

## Load Fixture Data
     python manage.py loaddata fixture/usertype.json
     python manage.py loaddata fixture/activitytype.json
     
