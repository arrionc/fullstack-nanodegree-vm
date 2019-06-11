# Catalog App 
This web app was created as part of the Fullstack Web Developer Nanodegree from Udacity.

The app lets you navigate through a number of categories providing a list of items for each one.
It will also provide a user registration and authentication system using your google credentials. Registered users will have the ability to post, edit and delete their own items 

The app also implements a JSON endpoints that serve the same information as displayed in the HTML endpoints for an arbitrary category or item in the catalog.

## Requirements:

- [Python](https://www.python.org/)
- [Flask](http://flask.pocoo.org/)
- [SqlAlchemy](https://www.sqlalchemy.org/)
- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/) or a Linux-based virtual machine
- [oauth2client](https://github.com/googleapis/oauth2client)
- [Bootstrap4](https://getbootstrap.com/)

## Setting up the environment:

- Install Vagrant and VirtualBox
- Clone the [fullstack-nanodegree-vm](https://github.com/arrionc/fullstack-nanodegree-vm) from GitHub
- Launch the Vagrant VM (vagrant up) and vagrant ssh
- Access the web app locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
- Run ```database_setup.py``` to set up the database
- Run ```starterItems.py``` to populate the database with starter items. 

## Run the application

- Run the application within the VM (python /vagrant/catalog/application.py)
-  Access and test your application by visiting http://localhost:8000 locally

## API Endpoints

| Request | Result |
|:----      |:---    |
|/regions/JSON| All the regions|
|/region/*region_id*/wines/JSON| All the wines in a region|
|/region/*region_id*/wine/*wine_id*/JSON| Specific wine info

