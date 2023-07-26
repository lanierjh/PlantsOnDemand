# Importing necessary modules
import os
import pathlib
import flask
from flask import Flask, redirect, url_for, request, render_template, session, abort, jsonify
import secrets
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import os
import pathlib
import requests
from cachecontrol import CacheControl
import requests
from pip._vendor import cachecontrol
import google.auth.transport.requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from googleapiclient.errors import HttpError


# Creating a Flask application instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PlantsOnDemand.db'
db = SQLAlchemy(app)

# Initialize Flask-Migrate
# will help manage  changes to db schema in systematic way over time by automating the process of generating database migration scripts.
#migrate = Migrate(app, db) couldn't download, will do nxt time 

# first we wanna save the session dat
# then we'll figure out how to retrieve the session data 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    picture = db.Column(db.String(250), unique=True, nullable=False)
    googleId = db.Column(db.String(255), unique=True, nullable=False)
    # a way for us to specify a relationship btwn the user and their many plants
    plants = db.relationship('UsersPlants', back_populates='user')
    log = db.relationship('PlantLog', back_populates='user')
    
class PlantLog(db.Model):
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #plants = db.relationship('UsersPlants', back_populates='log')
    user = db.relationship('User', back_populates='log')
    
class UsersPlants(db.Model):
    # make sure we get a value at least for common name and scientific name 
    plant_id = db.Column(db.Integer, primary_key=True, nullable=False)
    common_name = db.Column(db.String(250), nullable=False)
    nickname = db.Column(db.String(250))
    scientific_name = db.Column(db.Text, nullable=False)
    other_names = db.Column(db.Text)
    family = db.Column(db.String(100))
    origin = db.Column(db.Text)
    # like - is it a tree, ..etc 
    plant_type = db.Column(db.String(100))
    # will tell u height alone
    dimension = db.Column(db.String(100))
    #tell you type of dimension and max and min val
    # hv to flesh this out more extract min+unitand max +unit
    dimensions = db.Column(db.Text)
    cycle = db.Column(db.String(100))
    watering = db.Column(db.String(100))
    depth_water_requirement = db.Column(db.Text)
    volume_water_requirement = db.Column(db.Text)
    watering_period = db.Column(db.String(100))
    watering_general_benchmark = db.Column(db.String(100))
    default_image_url = db.Column(db.String(250))
    propagation = db.Column(db.String(250))
    maintenance = db.Column(db.String(100))
    care_level = db.Column(db.String(100))
    care_guides = db.Column(db.String(250))
    pruning_month = db.Column(db.String(250))
    pruning_count = db.Column(db.Integer)
    seeds = db.Column(db.Integer)
    flowering_season = db.Column(db.String(100))
    flowering_color = db.Column(db.String(100))
    cones = db.Column(db.String(200)) #once a boolean
    fruits = db.Column(db.String(200))
    edible_fruit = db.Column(db.String(200))
    edible_leaf = db.Column(db.String(200))
    medicinal = db.Column(db.String(200))
    poisonous_to_humans = db.Column(db.String(200)) #this one is an integer
    poisonous_to_pets = db.Column(db.String(200)) #this one is an integer
    description = db.Column(db.Text)
    hardiness_min = db.Column(db.String(10))
    hardiness_max = db.Column(db.String(10))
    hardiness_map = db.Column(db.Text)
    # Soil info
    soil = db.Column(db.Text)  # If there are multiple soil types, we can store them as a string
    #"drought_tolerant": false
    # Add fields for storing the reminder preferences
    reminder_frequency = db.Column(db.String(50))
    reminder_time = db.Column(db.String(10))
    reminder_day = db.Column(db.String(20))
    
     # Add the 'access_token' column to the table to allow us to store Google calendar access token for each plant 
    # it is required to create a Google Calendar event for plant reminder
    access_token = db.Column(db.String(250))
    refresh_token = db.Column(db.String(250))

    #this is a very good dataset, if we wanted to expand on this we could use the fields abv
    # as somewhat of a filter
    #0: Represents "false" or "off" in boolean context.
    #1: Represents "true" or "on" in boolean context.
    # way for us to connect to the User model wholistically:
    # Add the user_id column as a foreign key to the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='plants')

    
# Generating a secret key using the secrets module (not currently used in the code)
secret_key = secrets.token_hex(32)
#print(secret_key)


# Google Client ID obtained from the Google Developer Console
GOOGLE_CLIENT_ID = "138083707001-9rt68g745qcbjuhisjumsf6hnle2111s.apps.googleusercontent.com"


# Constructing the path for the 'client_secret.json' file using the pathlib module
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

    

# Creating a Flow instance for OAuth 2.0 authentication with Google
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
            "https://www.googleapis.com/auth/calendar"],
    redirect_uri="http://127.0.0.1:5000/callback"
)
# "https://www.googleapis.com/auth/user.addresses.read" maybe if we decide to add the location another useful one owould be calendar


# Creating a decorator function that checks if the user is in session before accessing protected areas
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function(*args, **kwargs)  # Pass the arguments to the decorated function
    # Rename the endpoint to avoid conflicts unlike original
    wrapper.__name__ = f"{function.__name__}_decorated"
    return wrapper




# Route for displaying the login page
@app.route("/login_page")
def login_page():
    return render_template("login.html")


# Route for initiating the login process with Google OAuth
@app.route("/login/google")
def login():
    if 'saved_plants' not in session:
        session['saved_plants'] = []
        print("create saved plants if user doesn't have")
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    # This function should handle data received from Google endpoint
    # An "endpoint" is a specific URL on a web server where data can be accessed.
    # In this case, Google's OAuth 2.0 endpoint is where the user is redirected
    # after granting permission to your application.

    # Fetch the access token from Google after the user grants permission
    flow.fetch_token(authorization_response=request.url)

    # Checking if the state returned by Google matches the one stored in the session
    if not session["state"] == request.args["state"]:
        abort(500) # state doesn't match

    # Obtaining the credentials containing the access token and other information
    credentials = flow.credentials

    # Create a request session with caching for better performance
    request_session = requests.Session()
    cached_session = CacheControl(request_session)
    token_request = Request(session=cached_session)

    # Verify the ID token to get user information
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )


    # Save user information in the session for future use
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["picture"] = id_info.get("picture") 
    # we need to save the credentials to session for later user in add_plant()
    session["credentials"] = {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
    }
    #print(id_info)
    #session["email_adress"] = id_info.get("e")
    user = User.query.filter_by(googleId=session["google_id"]).first()
    # Jackson u were right it's !user cz user alone means that there is something in user, I apologize!!!
    if not user:
        print("we create new user") 
        # wanna make sure we save the data into a db 
        new_user = User(
            googleId=session["google_id"], 
            name=session["name"], 
            email=session["email"],
            picture=session["picture"]
            )
        db.session.add(new_user)
        db.session.commit()
    # if the user has an account we want to restore the previous user data 
    # if the user has an account, we want to restore the previous user data we'll do this in user_profile and protected area
    # Redirect to the protected area after successful authentication
    return redirect("/protected_area")


# Route to clear the local session for the user (log out)
# just redirects to home page
@app.route("/signout")
def logout():
    session.clear()
    return redirect("/")

# Route for the home page
@app.route("/")
def home():
    return render_template('home.html')

# Route for displaying the protected area after successful login
@app.route("/protected_area")
@login_is_required
def protected_area():
    # for this dashboard we wanna query by id first then save the plants aft 
    user = User.query.filter_by(googleId=session["google_id"]).first()
    if user:
        saved_plants = user.plants  # Get the plants associated with the user
        saved_log = user.log
    else:
        saved_plants = []  # Initialize an empty list when the user has no plants
    #in the return statement, we want to pass the saved_plants into the user template where each column should be accessible 
    return render_template('protected_area.html', user=user, saved_plants=saved_plants, saved_log=saved_log)

@app.route('/plant_search', methods=['POST', 'GET'])
def plant_search():
    #note you'll get an error whenever you click navbar if u don't specify method
    if request.method == 'POST':
        plant_name = request.form['plant_name']
        care_level = request.form['care_level'] 
        # we perform our search below:
        
        # response
        response = requests.get('https://perenual.com/api/species-list?key=sk-x2Xs64bb0058c865e1636&q='+plant_name)

        result = response.json()
        newRes = result['data']
        
        #initialize some vars we'll be using later 
        index = 0
        output = None 
        # if the searcher doesn't care about the care level, we want to output the json as it is 
        if care_level == 'N/A':
            output = newRes
        else: 
            #otherwise we want to filter the output of newRes to suit the carelevel the user wants
            #here, we want to use a while loop: 
            output = []
            while index < len(newRes):
                id= newRes[index]['id']
                idStr = str(newRes[index]['id'])
                levelResponse = requests.get('https://perenual.com/api/species/details/'+idStr+'?key=sk-x2Xs64bb0058c865e1636')
                levelResult = levelResponse.json()
                print(levelResult)
                if care_level == levelResult["care_level"]:
                    # here we get the result from using that exact id to search if it's care_level matches the users wants:
                    print(levelResult)
                    output.append(levelResult)
                #Increase idx so that we don't enter infinite while loop
                index += 1
        return render_template('plant_search.html', plant_name=plant_name, care_level=care_level, search_results=output)
    return render_template('plant_search.html')

@app.route('/plant_details/<int:plant_id>', methods=['POST', 'GET'])
def plant_details(plant_id):
    # Get specific plant details using plant_id
    response = requests.get(f'https://perenual.com/api/species/details/{plant_id}?key=sk-x2Xs64bb0058c865e1636')
    plant_details = response.json()
    return render_template('plant_details.html', plant=plant_details)

# drum roll ---- we might just finally add these plants! 
@app.route('/add_plant', methods=["POST"])
@login_is_required
def add_plant():
    #check if the user is logged in
    #retrieve form data 
    plant_id = request.form.get('plant_id')
    common_name = request.form.get('common_name')
    scientific_name = request.form.get('scientific_name')
    nickname = request.form.get('nickname')  # Add other fields for the data you want to add to the database
    other_names = request.form.get('other_names')
    family = request.form.get('family')
    origin = request.form.get('origin')
    plant_type = request.form.get('plant_type')
    dimension = request.form.get('dimension')
    dimensions = request.form.get('dimensions')
    cycle = request.form.get('cycle')
    watering = request.form.get('watering')
    depth_water_requirement = request.form.get('depth_water_requirement')
    volume_water_requirement = request.form.get('volume_water_requirement')
    watering_period = request.form.get('watering_period')
    watering_general_benchmark = request.form.get('watering_general_benchmark')
    default_image_url = request.form.get('default_image_url')
    propagation = request.form.get('propagation')
    maintenance = request.form.get('maintenance')
    care_level = request.form.get('care_level')
    care_guides = request.form.get('care_guides')
    pruning_month = request.form.get('pruning_month')
    pruning_count = request.form.get('pruning_count')
    seeds = request.form.get('seeds')
    flowering_season = request.form.get('flowering_season')
    flowering_color = request.form.get('flowering_color')
    cones = request.form.get('cones')
    fruits = request.form.get('fruits')
    edible_fruit = request.form.get('edible_fruit')
    edible_leaf = request.form.get('edible_leaf')
    medicinal = request.form.get('medicinal')
    poisonous_to_humans = request.form.get('poisonous_to_humans')
    poisonous_to_pets = request.form.get('poisonous_to_pets')
    description = request.form.get('description')
    hardiness_min = request.form.get('hardiness_min')
    hardiness_max = request.form.get('hardiness_max')
    hardiness_map = request.form.get('hardiness_map')
    soil = request.form.get('soil')
    
    # we wanna check if the plant with that given id already exists for the user
    user = User.query.filter_by(googleId=session["google_id"]).first()
    #in the case where the user isn't found we want to throw an error
    if not user:
        return "User not found!", 404
    #I predict this might cause problems in that if the db is deleted and someone has cache or cookies 
    # they might log in but their info might not be added>>>>or do we acc for tt?
    # we won't find their info and an error will be thrown 
    
    # We also need to check if the user has authenticated with Google Calendar
    # and get the access_token and refresh_token from the credentials
       # We also need to check if the user has authenticated with Google Calendar
    # and get the access_token and refresh_token from the credentials
    if "credentials" in session:
        credentials_data = session["credentials"]
        access_token = credentials_data["access_token"]
        refresh_token = credentials_data["refresh_token"]
    else:
        # case when the user hasn't authenticated with Google Calendar
        access_token = None
        refresh_token = None
    
    
    existing_plant = UsersPlants.query.filter_by(user=user,plant_id=plant_id).first()
    
    if existing_plant:
        # if the plant already exists we can choose to update it's data or throw error
        if nickname:
            existing_plant.nickname = nickname 
        # we hope this update feature works, but if not, we have backup
        try:
            db.session.commit()
            return redirect("/user_profile")
        except Exception as e:
            #find way to handle errors or log error for debug purposes 
            # also want to undo changes made : might wanna make a def function for this 
            db.session.rollback()
            return "Error: Failed to update. Try again.", 500
    else:
        # Create a new UsersPlants object and add it to the database
        new_plant = UsersPlants(
            plant_id=plant_id,
            common_name=common_name,
            scientific_name=scientific_name,
            nickname=nickname,  # Add other fields for the data you want to add to the database
            other_names=other_names,
            family=family,
            origin=origin,
            plant_type=plant_type,
            dimension=dimension,
            dimensions=dimensions,
            cycle=cycle,
            watering=watering,
            depth_water_requirement=depth_water_requirement,
            volume_water_requirement=volume_water_requirement,
            watering_period=watering_period,
            watering_general_benchmark=watering_general_benchmark,
            default_image_url=default_image_url,
            propagation=propagation,
            maintenance=maintenance,
            care_level=care_level,
            care_guides=care_guides,
            pruning_month=pruning_month,
            pruning_count=pruning_count,
            seeds=seeds,
            flowering_season=flowering_season,
            flowering_color=flowering_color,
            cones=cones,
            fruits=fruits,
            edible_fruit=edible_fruit,
            edible_leaf=edible_leaf,
            medicinal=medicinal,
            poisonous_to_humans=poisonous_to_humans,
            poisonous_to_pets=poisonous_to_pets,
            description=description,
            hardiness_min=hardiness_min,
            hardiness_max=hardiness_max,
            hardiness_map=hardiness_map,
            soil=soil,
            access_token=access_token,
            refresh_token=refresh_token
        )   
        # #User.plants.append(new_plant)
        # db.session.add(new_plant)
        
        # #make sure we don't lose this info we've stored
        # db.session.commit()
        # Add the new plant to the user's list of plants
        user.plants.append(new_plant)
        # we hope this update feature works, but if not, we have backup
        try:
            db.session.commit()
            return redirect("/user_profile")
        except Exception as e:
            #find way to handle errors or log error for debug purposes 
            db.session.rollback()
            return "Error: Failed to update. Try again.", 500
    
    return redirect("/user_profile")    

def create_google_calendar_event(plant, event_data, user_timezone):
    print(user_timezone)
    # Check if the access token is expired
    credentials = Credentials(
        token=plant.access_token,
        refresh_token=plant.refresh_token,
        token_uri=flow.client_config['token_uri'],
        client_id=flow.client_config['client_id'],
        client_secret=flow.client_config['client_secret']
    )

    if credentials.expired:
        # Refresh the access token
        credentials.refresh(Request())

        # Update the plant's access token with the new one
        plant.access_token = credentials.token
        db.session.commit()

    # Create a service object to interact with the Google Calendar API
    service = build('calendar', 'v3', credentials=credentials)

    # Prepare the start and end date and time for the event
    start_datetime = datetime.now()
    end_datetime = start_datetime + timedelta(days=30)  # The reminder will stop a month later

    # Format the date and time strings as required by the Google Calendar API (in ISO 8601 format)
    start_time_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')

    # Create the event
    event = {
        'summary': f'Watering Reminder for {plant.common_name}',
        'description': f'Remember to water your {plant.common_name} plant.',
        'start': {
            'dateTime': start_time_str,
            'timeZone': user_timezone,
        },
        'end': {
            'dateTime': end_time_str,
            'timeZone': user_timezone,
        },
    }
    print(event)
    try:
        # Set the 'calendarId' to 'primary' to create the event in the user's primary calendar
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event
    except HttpError as e:
        # Handle the case when there is an HTTP error, such as missing time zone definition
        error_details = e._get_reason() if hasattr(e, '_get_reason') else str(e)
        return f"Error creating event: {error_details}"
    
    
@app.route('/user_profile')
@login_is_required
def user_profile():
    # Render the user_profile.html template for the user profile page
    # the google id is our  helper thruout
    # for this dashboard we wanna query by id first then save the plants aft 
    user = User.query.filter_by(googleId=session["google_id"]).first()
    if user:
        saved_plants = user.plants  # Get the plants associated with the user
    else:
        saved_plants = []  # Initialize an empty list when the user has no plants
    return render_template('user_profile.html', user=user, saved_plants=saved_plants)

@app.route('/plant_write', methods=['POST', 'GET'])
def plant_write():
    if request.method == 'POST':
    # Render the plant_diary.html template for the plant diary page
        title = request.form.get('title')
        date = request.form.get('date') 
        notes = request.form.get('notes')

        new_note = PlantLog(title=title,
                            date=date,
                            notes=notes)

        user = User.query.filter_by(googleId=session["google_id"]).first()
        user.log.append(new_note)
        db.session.commit()
    
    return render_template('plant_write.html')

@app.route('/add_reminder/<int:plant_id>', methods=['POST', 'GET'])
def add_reminder(plant_id):
    # Get specific plant details using plant_id
    current_user = User.query.filter_by(googleId=session["google_id"]).first()

    plant = UsersPlants.query.filter_by(user=current_user, plant_id=plant_id).first()

    if not plant:
        # Handle the case when the plant with the given plant_id is not found just in case, but wedon't anticipate this hpning 
        return render_template('error.html', error_message="Plant not found")

    if request.method == 'POST':
        # Retrieve the form data for reminder preferences
        reminder_frequency = request.form['reminder_frequency']
        reminder_time = request.form['reminder_time']
        user_timezone = "America/New_York"
        
        print(user_timezone)

        if reminder_frequency == 'weekly':
            # If the reminder is set to "Weekly," retrieve the selected day from the form
            
            reminder_day = request.form.get('reminder_day')
            # Check if the user selected a day, if not, set reminder_day to None
            if not reminder_day or reminder_day == 'default_if_none':
                plant.reminder_day = None
            else:
                plant.reminder_day = reminder_day
                
            # Update the plant's reminder preferences for weekly reminders
            plant.reminder_frequency = reminder_frequency
            plant.reminder_time = reminder_time
        else:
            # For daily  reminders, only update frequency and time
            plant.reminder_frequency = reminder_frequency
            plant.reminder_time = reminder_time

        # Commit changes to the database
        db.session.commit()
        
        # Prepare the event data for creating the Google Calendar event
        event_data = create_event_data(plant, user_timezone)

        # Call the create_google_calendar_event function to add the reminder to the user's Google Calendar
        # Pass the plant object and the event_data to the function
        create_google_calendar_event(plant, event_data, user_timezone)
        # Redirect to the user profile page or any other appropriate page
        return redirect("/protected_area")

    return render_template('add_reminder.html', plant=plant)

def create_event_data(plant, user_timezone):
    print(user_timezone)
    event_data = {}

    # Get current date and time
    current_datetime = datetime.now()

    # Calculate the end date by adding one month to the current date using timedelta
    end_datetime = current_datetime + timedelta(days=30)

    # Format dates in the required format (YYYY-MM-DDTHH:mm:00) e.g., 2023-07-23T10:30:00
    start_datetime_str = current_datetime.strftime("%Y-%m-%dT%H:%M:00")
    end_datetime_str = end_datetime.strftime("%Y-%m-%dT%H:%M:00")

    # Check if the reminder is set to "Weekly"
    if plant.reminder_frequency == "weekly":
        # Make sure the reminder_day is not empty
        if plant.reminder_day:
            # Add the day and time to the event_data for a weekly reminder
            event_data['start_datetime'] = start_datetime_str
            event_data['end_datetime'] = end_datetime_str
            event_data['recurrence'] = [
                f"RRULE:FREQ=WEEKLY;BYDAY={plant.reminder_day.upper()}"
            ]
        else:
            # If the reminder_day is not set, we will fallback to a daily reminder
            event_data['start_datetime'] = start_datetime_str
            event_data['end_datetime'] = end_datetime_str
    else:
        # For daily reminders, just use the reminder_time and date for a single event
        event_data['start_datetime'] = start_datetime_str
        event_data['end_datetime'] = end_datetime_str

    return event_data

@app.route('/plant_diary')
def plant_diary():
    
    user = User.query.filter_by(googleId=session["google_id"]).first()
    if user:
        saved_notes = user.log  # Get the plants associated with the user
    else:
        saved_notes = []  # Initialize an empty list when the user has no plants
    return render_template('plant_diary.html', user=user, saved_notes=saved_notes)

@app.route('/diary_delete/<int:log_id>')
def diary_delete(log_id):
    deleted_log = PlantLog.query.get_or_404(log_id)
    db.session.delete(deleted_log)
    db.session.commit()
    
    return redirect('/plant_diary')

@app.route('/open_note/<int:log_id>')
def open_diary(log_id):
    opened_log = PlantLog.query.get_or_404(log_id)
    
    
    return render_template('/open_note.html', note=opened_log)

@app.route('/plant_simulation')
def plant_simulation():
    # Render the plant_simulation.html template for the plant simulation page
    return render_template('plant_simulation.html')

@app.route('/error')
def error():
    # Render the error.html template for the error page
    return render_template('error.html')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Override the OAUTHLIB_INSECURE_TRANSPORT variable for local development
    # this is a quick fix to it for only local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
   
    # Setting the app's secret key for session management: might have questions about the security of this procedure?
    app.secret_key = "a16d378de074a6f025a0015ebbf8c490dbfa6e2545436920823c6248c2f53256"
    # Running the Flask application in debug mode
    app.run(debug=True)
    
    

  



  
