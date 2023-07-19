from flask import Flask, jsonify, request, render_template

app = Flask(__name__) 

# plant_health = 100 


@app.route('/')
def page():
    return render_template('page.html')

@app.route('/api/water', methods=['POST'])
def water_plant():
    # global plant_health
    data = request.get_json()
    plant_health = data.get('plant_health', 100)
    plant_health += 10 
    if plant_health > 100: 
        plant_health = 100
    return jsonify({'plant_health': plant_health})

@app.route('/api/sunlight', methods=['POST'])
def give_sunlight():
    # global plant_health
    data = request.get_json()
    plant_health = data.get('plant_health', 100)
    plant_health += 10
    if plant_health > 100: 
        plant_health = 100
    return jsonify({'plant_health': plant_health})

@app.route('/api/fertilize', methods=['POST'])
def give_fertilizer():
    # global plant_health
    data = request.get_json()
    plant_health = data.get('plant_health', 100)
    plant_health += 15
    if plant_health > 100: 
        plant_health = 100
    return jsonify({'plant_health': plant_health})

if __name__ == '__main__':
    app.run(debug=True)