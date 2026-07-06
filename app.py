from flask import Flask, render_template, Response, jsonify, request
from core import AirLightCore
import time

app = Flask(__name__)
airlight = AirLightCore()

# We start the core AirLight background loop
airlight.start()

def generate_frames():
    """Generator function to yield JPEG frames from the OpenCV stream"""
    while True:
        frame_bytes = airlight.get_jpeg_frame()
        if frame_bytes is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.01)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify(airlight.get_status())

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    airlight.ping_heartbeat()
    return jsonify({"status": "ok"})

@app.route('/api/action', methods=['POST'])
def action():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400
        
    action_type = data.get('type')
    val = data.get('value')
    
    if action_type == 'color':
        airlight.bulb.set_color(val)
        airlight.mapper.last_color = val
    elif action_type == 'rgb':
        airlight.bulb.set_rgb(val.get('r'), val.get('g'), val.get('b'))
        airlight.mapper.last_color = "custom"
    elif action_type == 'brightness':
        bval = int(val)
        airlight.bulb.set_brightness(bval)
        airlight.mapper.last_brightness = bval
    elif action_type == 'saturation':
        sval = float(val)
        airlight.bulb.set_saturation(sval)
        airlight.mapper.last_saturation = sval
    elif action_type == 'power':
        if val == 'on':
            airlight.bulb.turn_on()
            airlight.mapper.last_power_state = True
        else:
            airlight.bulb.turn_off()
            airlight.mapper.last_power_state = False
    elif action_type == 'scene':
        airlight.bulb.set_scene(int(val))
            
    return jsonify({"status": "success"})

@app.route('/api/readme')
def get_readme():
    try:
        with open('README.md', 'r') as f:
            return jsonify({"content": f.read()})
    except:
        return jsonify({"content": "README not found."})

@app.route('/api/scenes')
def get_scenes():
    # Return 4 local mock scenes supported by tinytuya local API
    return jsonify({
        "scenes": [
            {"id": 1, "name": "Nightlight", "icon": "bedtime", "description": "Dim warm glow for night time."},
            {"id": 2, "name": "Reading", "icon": "menu_book", "description": "Bright focused white light."},
            {"id": 3, "name": "Working", "icon": "work", "description": "Crisp daylight for concentration."},
            {"id": 4, "name": "Leisure", "icon": "coffee", "description": "Relaxed ambient coloring."}
        ]
    })

if __name__ == '__main__':
    try:
        # Run Flask server
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    finally:
        airlight.stop()
