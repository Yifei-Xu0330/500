from flask import Flask, render_template, request
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

EARTH_RADIUS = 6371000

def dms_to_decimal(degrees, minutes, seconds, direction):

    decimal = float(degrees) + float(minutes)/60 + float(seconds)/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def decimal_to_dms(decimal):

    degrees = int(decimal)
    minutes_decimal = (decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    
    direction = 'N'
    if degrees < 0:
        direction = 'S'
    degrees = abs(degrees)
    
    return degrees, minutes, seconds, direction

def calculate_distance(point1, point2):


    lat1, lon1, alt1 = point1
    lat2, lon2, alt2 = point2

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    surface_distance = EARTH_RADIUS * c
    
    r1 = EARTH_RADIUS + alt1
    r2 = EARTH_RADIUS + alt2
    
    x1 = r1 * math.cos(lat1_rad) * math.cos(lon1_rad)
    y1 = r1 * math.cos(lat1_rad) * math.sin(lon1_rad)
    z1 = r1 * math.sin(lat1_rad)
    
    x2 = r2 * math.cos(lat2_rad) * math.cos(lon2_rad)
    y2 = r2 * math.cos(lat2_rad) * math.sin(lon2_rad)
    z2 = r2 * math.sin(lat2_rad)
    
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    straight_distance = math.sqrt(dx**2 + dy**2 + dz**2)
    
    return surface_distance, straight_distance

def create_plot(point1, point2):

    fig = plt.figure(figsize=(10, 5))
    
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.set_title("地球表面视图")
    
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = EARTH_RADIUS * np.outer(np.cos(u), np.sin(v))
    y = EARTH_RADIUS * np.outer(np.sin(u), np.sin(v))
    z = EARTH_RADIUS * np.outer(np.ones(np.size(u)), np.cos(v))
    
    ax1.plot_surface(x, y, z, color='b', alpha=0.1)

    lat1, lon1, alt1 = point1
    lat2, lon2, alt2 = point2
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    r1 = EARTH_RADIUS + alt1
    r2 = EARTH_RADIUS + alt2
    
    x1 = r1 * math.cos(lat1_rad) * math.cos(lon1_rad)
    y1 = r1 * math.cos(lat1_rad) * math.sin(lon1_rad)
    z1 = r1 * math.sin(lat1_rad)
    
    x2 = r2 * math.cos(lat2_rad) * math.cos(lon2_rad)
    y2 = r2 * math.cos(lat2_rad) * math.sin(lon2_rad)
    z2 = r2 * math.sin(lat2_rad)
    
    ax1.scatter([x1, x2], [y1, y2], [z1, z2], c='r', s=50)
    ax1.plot([x1, x2], [y1, y2], [z1, z2], 'r-', linewidth=2)
    
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    
    ax2 = fig.add_subplot(122)
    ax2.set_title("经纬度视图")

    earth_circle = plt.Circle((0, 0), EARTH_RADIUS, color='b', alpha=0.1)
    ax2.add_patch(earth_circle)

    ax2.scatter([lon1_rad * EARTH_RADIUS, lon2_rad * EARTH_RADIUS], 
                [lat1_rad * EARTH_RADIUS, lat2_rad * EARTH_RADIUS], 
                c='r', s=50)
    
    ax2.plot([lon1_rad * EARTH_RADIUS, lon2_rad * EARTH_RADIUS], 
             [lat1_rad * EARTH_RADIUS, lat2_rad * EARTH_RADIUS], 
             'r-', linewidth=2)
    
    ax2.set_xlim(-EARTH_RADIUS * 1.2, EARTH_RADIUS * 1.2)
    ax2.set_ylim(-EARTH_RADIUS * 1.2, EARTH_RADIUS * 1.2)
    ax2.set_aspect('equal')
    ax2.set_xlabel('经度方向 (m)')
    ax2.set_ylabel('纬度方向 (m)')
    
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("收到表单提交！")
        print(request.form)
        input_format = request.form.get('input_format')
        
        if input_format == 'dms':
            lat1_deg = request.form.get('lat1_deg')
            lat1_min = request.form.get('lat1_min')
            lat1_sec = request.form.get('lat1_sec')
            lat1_dir = request.form.get('lat1_dir')
            lon1_deg = request.form.get('lon1_deg')
            lon1_min = request.form.get('lon1_min')
            lon1_sec = request.form.get('lon1_sec')
            lon1_dir = request.form.get('lon1_dir')
            alt1 = float(request.form.get('alt1'))
            
            lat1 = dms_to_decimal(lat1_deg, lat1_min, lat1_sec, lat1_dir)
            lon1 = dms_to_decimal(lon1_deg, lon1_min, lon1_sec, lon1_dir)
        else:  
            lat1 = math.degrees(float(request.form.get('lat1_rad')))
            lon1 = math.degrees(float(request.form.get('lon1_rad')))
            alt1 = float(request.form.get('alt1'))

        if input_format == 'dms':
            lat2_deg = request.form.get('lat2_deg')
            lat2_min = request.form.get('lat2_min')
            lat2_sec = request.form.get('lat2_sec')
            lat2_dir = request.form.get('lat2_dir')
            lon2_deg = request.form.get('lon2_deg')
            lon2_min = request.form.get('lon2_min')
            lon2_sec = request.form.get('lon2_sec')
            lon2_dir = request.form.get('lon2_dir')
            alt2 = float(request.form.get('alt2'))
            
            lat2 = dms_to_decimal(lat2_deg, lat2_min, lat2_sec, lat2_dir)
            lon2 = dms_to_decimal(lon2_deg, lon2_min, lon2_sec, lon2_dir)
        else:  # radians
            lat2 = math.degrees(float(request.form.get('lat2_rad')))
            lon2 = math.degrees(float(request.form.get('lon2_rad')))
            alt2 = float(request.form.get('alt2'))
        
        point1 = (lat1, lon1, alt1)
        point2 = (lat2, lon2, alt2)
        surface_dist, straight_dist = calculate_distance(point1, point2)
        
        plot_url = create_plot(point1, point2)
        
        lat1_dms = decimal_to_dms(lat1)
        lon1_dms = decimal_to_dms(lon1)
        
        lat2_dms = decimal_to_dms(lat2)
        lon2_dms = decimal_to_dms(lon2)
        
        return render_template('index.html', 
                               input_format=input_format,
                               point1=point1,
                               point2=point2,
                               lat1_dms=lat1_dms,
                               lon1_dms=lon1_dms,
                               lat2_dms=lat2_dms,
                               lon2_dms=lon2_dms,
                               surface_dist=surface_dist,
                               straight_dist=straight_dist,
                               plot_url=plot_url)
    
    return render_template('index.html', input_format='dms')

if __name__ == '__main__':
    app.run(debug=True)