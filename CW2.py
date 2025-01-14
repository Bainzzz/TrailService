from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import pyodbc


app = Flask(__name__)
api = Api(app)


DB_CONFIG = {
    "server": "dist-6-505.uopnet.plymouth.ac.uk",
    "database": "COMP2001_SBains",
    "username": "SBains",
    "password": "VdaI735*",
}

def get_db_connection():
    connection = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
    )
    return connection

    
class AddTrail(Resource):
    def post(self):
        data = request.get_json()

        # Extract details from the request data
        trail_name = data['TrailName']
        trail_summary = data['TrailSummary']
        trail_description = data['TrailDescription']
        difficulty = data['Difficulty']
        location = data['Location']
        length = data['Length']
        elevation_gain = data['ElevationGain']
        route_type = data['RouteType']
        owner_id = data['OwnerID']

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            EXEC CW2.AddTrail ?, ?, ?, ?, ?, ?, ?, ?, ?
        """, (trail_name, trail_summary, trail_description, difficulty, location, length, elevation_gain, route_type, owner_id))
        
        conn.commit()
        conn.close()

        return jsonify({"message": "Trail added successfully!"}), 201


# Get all Trails - corresponding to GetAllTrails stored procedure
class GetAllTrails(Resource):
    def get(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("EXEC CW2.GetAllTrails")
        rows = cursor.fetchall()

        trails = []
        for row in rows:
            trails.append(dict(zip([column[0] for column in cursor.description], row)))
        
        conn.close()
        return jsonify(trails)


# Delete Trail - corresponding to DeleteTrail stored procedure
class DeleteTrail(Resource):
    def delete(self, trail_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("EXEC CW2.DeleteTrail @TrailID = ?", (trail_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Trail deleted successfully!"})


# Update Trail - corresponding to UpdateTrail stored procedure
class UpdateTrail(Resource):
    def put(self, trail_id):
        data = request.get_json()

        
        trail_name = data['TrailName']
        trail_summary = data['TrailSummary']
        trail_description = data['TrailDescription']
        difficulty = data['Difficulty']
        location = data['Location']
        length = data['Length']
        elevation_gain = data['ElevationGain']
        route_type = data['RouteType']

    
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            EXEC CW2.UpdateTrail ?, ?, ?, ?, ?, ?, ?, ?, ?
        """, (trail_id, trail_name, trail_summary, trail_description, difficulty, location, length, elevation_gain, route_type))
        
        conn.commit()
        conn.close()

        return jsonify({"message": "Trail updated successfully!"})


# Get a single Trail by ID - corresponding to GetTrailByID stored procedure
class GetTrailByID(Resource):
    def get(self, trail_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("EXEC CW2.GetTrailByID @TrailID = ?", (trail_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            trail = dict(zip([column[0] for column in cursor.description], row))
            return jsonify(trail)
        else:
            return jsonify({"message": "Trail not found!"}), 404


# Add resources for the API
api.add_resource(AddTrail, '/trail')
api.add_resource(GetAllTrails, '/trails')
api.add_resource(DeleteTrail, '/trail/<int:trail_id>')
api.add_resource(UpdateTrail, '/trail/<int:trail_id>')
api.add_resource(GetTrailByID, '/trail/<int:trail_id>')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)