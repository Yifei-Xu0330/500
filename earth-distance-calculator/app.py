# app.py (简化版)
from flask import Flask, render_template, request
import math

app = Flask(__name__)
EARTH_RADIUS = 6371000  # 地球平均半径（米）

def dms_to_decimal(degrees, minutes, seconds, direction):
    """度分秒转十进制度"""
    decimal = float(degrees) + float(minutes)/60 + float(seconds)/3600
    return -decimal if direction in ['S', 'W'] else decimal

def calculate_distance(point1, point2):
    """计算两点间距离（考虑高度）"""
    lat1, lon1, alt1 = point1
    lat2, lon2, alt2 = point2
    
    # 转换为弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 球面距离（Haversine公式）
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    surface_distance = EARTH_RADIUS * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # 空间直线距离（考虑高度）
    r1 = EARTH_RADIUS + alt1
    r2 = EARTH_RADIUS + alt2
    x1 = r1 * math.cos(lat1_rad) * math.cos(lon1_rad)
    y1 = r1 * math.cos(lat1_rad) * math.sin(lon1_rad)
    z1 = r1 * math.sin(lat1_rad)
    x2 = r2 * math.cos(lat2_rad) * math.cos(lon2_rad)
    y2 = r2 * math.cos(lat2_rad) * math.sin(lon2_rad)
    z2 = r2 * math.sin(lat2_rad)
    straight_distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    
    return surface_distance, straight_distance

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        try:
            # 获取输入格式
            input_format = request.form.get('input_format', 'dms')
            
            # 处理点1坐标
            if input_format == 'dms':
                lat1 = dms_to_decimal(
                    request.form.get('lat1_deg', 0),
                    request.form.get('lat1_min', 0),
                    request.form.get('lat1_sec', 0),
                    request.form.get('lat1_dir', 'N')
                )
                lon1 = dms_to_decimal(
                    request.form.get('lon1_deg', 0),
                    request.form.get('lon1_min', 0),
                    request.form.get('lon1_sec', 0),
                    request.form.get('lon1_dir', 'E')
                )
            else:
                lat1 = math.degrees(float(request.form.get('lat1_rad', 0)))
                lon1 = math.degrees(float(request.form.get('lon1_rad', 0)))
            alt1 = float(request.form.get('alt1', 0))
            
            # 处理点2坐标（同上）
            if input_format == 'dms':
                lat2 = dms_to_decimal(
                    request.form.get('lat2_deg', 0),
                    request.form.get('lat2_min', 0),
                    request.form.get('lat2_sec', 0),
                    request.form.get('lat2_dir', 'N')
                )
                lon2 = dms_to_decimal(
                    request.form.get('lon2_deg', 0),
                    request.form.get('lon2_min', 0),
                    request.form.get('lon2_sec', 0),
                    request.form.get('lon2_dir', 'E')
                )
            else:
                lat2 = math.degrees(float(request.form.get('lat2_rad', 0)))
                lon2 = math.degrees(float(request.form.get('lon2_rad', 0)))
            alt2 = float(request.form.get('alt2', 0))
            
            # 计算距离
            surface_dist, straight_dist = calculate_distance(
                (lat1, lon1, alt1),
                (lat2, lon2, alt2)
            )
            
            # 准备结果
            results = {
                'point1': (lat1, lon1, alt1),
                'point2': (lat2, lon2, alt2),
                'surface_dist': surface_dist,
                'straight_dist': straight_dist
            }
        except Exception as e:
            results = {'error': f"计算错误: {str(e)}"}
    
    return render_template('index.html', results=results, input_format=input_format)

if __name__ == '__main__':
    app.run(debug=True, port=5001)