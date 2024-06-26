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


# Creating a Flask application instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PlantsOnDemand.db'
db = SQLAlchemy(app)


# first we wanna save the session dat
# then we'll figure out how to retrieve the session data 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    picture = db.Column(db.String(250), unique=True, nullable=False)
    googleId = db.Column(db.String(255), unique=True, nullable=False)
    # a way for us to create a relationship btwn the user and their many plants
    plants = db.relationship('UsersPlants', back_populates='user')
    
class UsersPlants(db.Model):
    # make sure we get a value at least for common name and scientific name 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    common_name = db.Column(db.String(250), nullable=False)
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
    cones = db.Column(db.Boolean)
    fruits = db.Column(db.Boolean)
    edible_fruit = db.Column(db.Boolean)
    edible_leaf = db.Column(db.Boolean)
    medicinal = db.Column(db.Boolean)
    poisonous_to_humans = db.Column(db.Boolean)
    poisonous_to_pets = db.Column(db.Boolean)
    description = db.Column(db.Text)
    hardiness_min = db.Column(db.String(10))
    hardiness_max = db.Column(db.String(10))
    hardiness_map = db.Column(db.Text)
    # Soil info
    soil = db.Column(db.Text)  # If there are multiple soil types, we can store them as a string
    
    #this is a very good dataset, if we wanted to expand on this we could use the fields abv
    # as somewhat of a filter
    

    # way for us to connect to the User model:
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
            "openid"],
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


# Define the route to handle adding a plant
@app.route('/add_plant', methods=['POST'])
def add_plant():
    if request.method == 'POST':
        plant_id = int(request.form.get('plant_id'))
        print(plant_id)
        # Check if the plant ID is already in the saved_plants list
        if plant_id in session['saved_plants']:
            print("I added", plant_id)
            return jsonify({'success': False, 'message': 'Plant already added.'})

        print(session['saved_plants'])
        # If the plant ID is not in the list, add it to the saved_plants list
        session['saved_plants'].append(plant_id)
        print(session['saved_plants'])
        # allow session mofification to be stored
        session.modified = True
        return jsonify({'success': True, 'message': 'Plant added successfully.'})

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
    if user:
        # Get user-specific data from the database (e.g., saved plants)
        saved_plants = saved_plants.query.filter(users_plants.id.in_(user.saved_plant_ids)).all()
        # restore user history
        session['saved_plants'] = saved_plants
        return render_template("protected_area.html", user=user, saved_plants=saved_plants)
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
#@login_is_required
def protected_area():
    return render_template('protected_area.html')


@app.route('/plant_search', methods=['GET', 'POST'])
def plant_search():
    output = ''
    if request.method == 'POST':
       
        # Get the user's search query from the form data
        plant_name = request.form.get('plant_name')
        care_level = request.form.get('care_level')
       
        # response
        response = requests.get('https://perenual.com/api/species-list?key=sk-x2Xs64bb0058c865e1636&q='+plant_name)

        result = response.json()
        newRes = result['data']
        index = 0
        session['search results'] = []
       
        while index < len(newRes):
            id = newRes[index]['id']
            idStr = str(id)
            out_id = ''
            if care_level != 'N/A':
                levelResponse = requests.get('https://perenual.com/api/species/details/'+idStr+'?key=sk-x2Xs64bb0058c865e1636')
                levelResult = levelResponse.json()
            
                if care_level == levelResult["care_level"]:
                    # addition: 
                    out_id = idStr
                    output += idStr + '\n'
                    #addition
                    common_name  =  newRes[index]['common_name']
                    output += newRes[index]['common_name']
                    output += '\n'
                    output += str(newRes[index]['scientific_name'])
                    #addition
                    scientific_names = newRes[index]['scientific_name']
                    output += '\n'
                    picture = newRes[index]['default_image']
                    if picture == None:
                        output += 'no url' + '\n'
                    else:
                        output += picture['original_url']
                        output += '\n'
                    #print()
                    output += '\n'
            else:
                # here we will acquire all the data possible for 
                output += idStr + '\n'
                output += newRes[index]['common_name']
                #addition
                common_name  =  newRes[index]['common_name']
                output += '\n'
                output += str(newRes[index]['scientific_name'])
                output += '\n'
                #addition
                scientific_names = newRes[index]['scientific_name']
                picture = newRes[index]['default_image']
                if picture == None:
                    #print("no_url")
                    output += 'no url' + '\n'
                else:
                    #print(picture['original_url'])
                    output += picture['original_url']
                    output += '\n'
                #print()
                output += '\n'
            index += 1
        #return render_template('plant_search.html', name=output)
       
        print(output2)
        print("/n".split(output))
        # For demonstration purposes, let's print the search parameters.
        # if plant_name:
        #     print('Search by Name:', plant_name)
        # if care_level:
        #     print('Search by Care Level:', care_level)


        #output2 = 
        # we'll put our json into a list of plants as search_results.
        search_results = [
            {plant_name: care_level}
        ]


        # Return the search_results to the template for displaying the results.
        return render_template('plant_search.html', search_results=search_results, name=output)


    # If it's a GET request, we render the plant_search.html template.
    return render_template('plant_search.html', name=output)




@app.route('/user_profile')
def user_profile():
    # Render the user_profile.html template for the user profile page
    return render_template('user_profile.html')


@app.route('/plant_diary')
def plant_diary():
    # Render the plant_diary.html template for the plant diary page
    return render_template('plant_diary.html')


@app.route('/plant_simulation')
def plant_simulation():
    # Render the plant_simulation.html template for the plant simulation page
    return render_template('plant_simulation.html')


@app.route('/plant_recommendations')
def plant_recommendations():
    # Get the user's search query from the form data
        plant_name = request.form.get('plant_name')
        care_level = request.form.get('care_level')
       
        # response
        response = requests.get('https://perenual.com/api/species-list?key=sk-L9aC64b73122e37dc1596&q='+plant_name)


        result = response.json()
        newRes = result['data']
        index = 0
        output = ''


        while index < len(newRes):
            id = newRes[index]['id']
            #print(id)
           
            idStr = str(id)
            output += idStr + '\n'
            #print(newRes[index]['common_name'])
            output += newRes[index]['common_name']
            output += '\n'
            #print(newRes[index]['scientific_name'])
            output += str(newRes[index]['scientific_name'])
            output += '\n'
            picture = newRes[index]['default_image']
            if picture == None:
                #print("no_url")
                output += 'no url' + '\n'
            else:
                #print(picture['original_url'])
                output += picture['original_url']
                output += '\n'
            #print()
            output += '\n'
            index += 1


        # Return the search_results to the template for displaying the results.
        return render_template('plant_search.html', name=output)


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
    
    

  



  