from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)


EARTH_RADIUS = 6371000

def dms_to_degrees(d, m, s):
    
    return d + m/60 + s/3600

def degrees_to_radians(deg):
    
    return deg * math.pi / 180

def dms_to_radians(d, m, s):
    
    return degrees_to_radians(dms_to_degrees(d, m, s))

def calculate_distance(lat1, lon1, h1, lat2, lon2, h2, mode):
    
    if mode == 'dms':
        
        lat1_rad = dms_to_radians(lat1[0], lat1[1], lat1[2])
        lon1_rad = dms_to_radians(lon1[0], lon1[1], lon1[2])
        lat2_rad = dms_to_radians(lat2[0], lat2[1], lat2[2])
        lon2_rad = dms_to_radians(lon2[0], lon2[1], lon2[2])
    else:  
        lat1_rad = lat1
        lon1_rad = lon1
        lat2_rad = lat2
        lon2_rad = lon2
    
    
    r1 = EARTH_RADIUS + h1
    r2 = EARTH_RADIUS + h2
    
    x1 = r1 * math.cos(lat1_rad) * math.cos(lon1_rad)
    y1 = r1 * math.cos(lat1_rad) * math.sin(lon1_rad)
    z1 = r1 * math.sin(lat1_rad)
    
    x2 = r2 * math.cos(lat2_rad) * math.cos(lon2_rad)
    y2 = r2 * math.cos(lat2_rad) * math.sin(lon2_rad)
    z2 = r2 * math.sin(lat2_rad)
    
    
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    
    return distance

@app.route('/', methods=['GET', 'POST'])
def index():
    distance = None
    if request.method == 'POST':
        mode = request.form['mode']
        
        try:
            if mode == 'dms':
                
                lat1 = [float(request.form['lat1_d']), float(request.form['lat1_m']), float(request.form['lat1_s'])]
                lon1 = [float(request.form['lon1_d']), float(request.form['lon1_m']), float(request.form['lon1_s'])]
                h1 = float(request.form['h1'])
                
                lat2 = [float(request.form['lat2_d']), float(request.form['lat2_m']), float(request.form['lat2_s'])]
                lon2 = [float(request.form['lon2_d']), float(request.form['lon2_m']), float(request.form['lon2_s'])]
                h2 = float(request.form['h2'])
                
                
                if not (-90 <= lat1[0] < 90 and -90 <= lat2[0] < 90):
                    raise ValueError("纬度必须在-90到90度之间")
                
                
                if not (-180 <= lon1[0] < 180 and -180 <= lon2[0] < 180):
                    raise ValueError("经度必须在-180到180度之间")
                
            else:  
                lat1 = float(request.form['lat1_rad'])
                lon1 = float(request.form['lon1_rad'])
                h1 = float(request.form['h1'])
                
                lat2 = float(request.form['lat2_rad'])
                lon2 = float(request.form['lon2_rad'])
                h2 = float(request.form['h2'])
                
                
                if not (-math.pi/2 <= lat1 <= math.pi/2 and -math.pi/2 <= lat2 <= math.pi/2):
                    raise ValueError("纬度必须在-π/2到π/2之间")
                
                
                if not (-math.pi <= lon1 <= math.pi and -math.pi <= lon2 <= math.pi):
                    raise ValueError("经度必须在-π到π之间")
            
            
            distance = calculate_distance(lat1, lon1, h1, lat2, lon2, h2, mode)
            
        except ValueError as e:
            distance = f"输入错误: {str(e)}"
        except Exception as e:
            distance = f"计算错误: {str(e)}"
    
    return render_template('index.html', distance=distance)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        mode = data['mode']
        
        if mode == 'dms':
            
            lat1 = [float(data['lat1_d']), float(data['lat1_m']), float(data['lat1_s'])]
            lon1 = [float(data['lon1_d']), float(data['lon1_m']), float(data['lon1_s'])]
            h1 = float(data['h1'])
            
            lat2 = [float(data['lat2_d']), float(data['lat2_m']), float(data['lat2_s'])]
            lon2 = [float(data['lon2_d']), float(data['lon2_m']), float(data['lon2_s'])]
            h2 = float(data['h2'])
            
            
            if not (-90 <= lat1[0] < 90 and -90 <= lat2[0] < 90):
                return jsonify({'error': "纬度必须在-90到90度之间"}), 400
            
            
            if not (-180 <= lon1[0] < 180 and -180 <= lon2[0] < 180):
                return jsonify({'error': "经度必须在-180到180度之间"}), 400
            
        else:  
            lat1 = float(data['lat1_rad'])
            lon1 = float(data['lon1_rad'])
            h1 = float(data['h1'])
            
            lat2 = float(data['lat2_rad'])
            lon2 = float(data['lon2_rad'])
            h2 = float(data['h2'])
            
            
            if not (-math.pi/2 <= lat1 <= math.pi/2 and -math.pi/2 <= lat2 <= math.pi/2):
                return jsonify({'error': "纬度必须在-π/2到π/2之间"}), 400
            
            if not (-math.pi <= lon1 <= math.pi and -math.pi <= lon2 <= math.pi):
                return jsonify({'error': "经度必须在-π到π之间"}), 400
        
        distance = calculate_distance(lat1, lon1, h1, lat2, lon2, h2, mode)
        
        return jsonify({
            'distance': distance,
            'formatted_distance': f"{distance:,.2f} 米"
        })
    
    except Exception as e:
        return jsonify({'error': f"计算错误: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)