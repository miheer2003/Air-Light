# 🛠️ Tuya Smart Bulb Setup Guide

AirLight uses **TinyTuya** to communicate locally with your smart bulb for zero-latency, cloud-free control. 

To achieve this, you need three pieces of information from your Tuya / Smart Life bulb:
1. **Device IP Address**
2. **Device ID**
3. **Local Key**

Getting the Local Key requires a one-time setup using the Tuya IoT Developer Platform. Follow these steps carefully.

---

## Step 1: Set up the Smart Life App
1. Download the **Tuya Smart** or **Smart Life** app on your phone.
2. Pair your Smart RGB Bulb with the app.
3. Ensure your phone and the bulb are on the **same 2.4GHz Wi-Fi network**.

## Step 2: Create a Tuya IoT Account
1. Go to the [Tuya IoT Platform](https://iot.tuya.com/) and create a developer account.
2. Go to **Cloud -> Development** and click **Create Cloud Project**.
   - **Industry**: Smart Home
   - **Development Method**: Custom
   - **Data Center**: Select your region (e.g., Western America). *Important: This must match your app's region.*
3. On the **Authorize API Services** step, ensure that **IoT Core**, **Authorization Token Management**, and **Smart Home Scene Linkage** are selected.

## Step 3: Link Your Devices to the Cloud Project
1. Inside your new Cloud Project, go to the **Devices** tab.
2. Click **Link Tuya App Account**.
3. Click **Add App Account** (this will show a QR code).
4. Open the **Smart Life** app on your phone, tap the scanner icon (top right), and scan the QR code to link your devices.

## Step 4: Run the TinyTuya Wizard
Now you will use TinyTuya's built-in wizard to fetch your Local Key automatically.

1. Open your terminal in the `Air-Light` project directory.
2. Ensure your virtual environment is activated, then run:
   ```bash
   python3 -m tinytuya wizard
   ```
3. The wizard will ask you for:
   - **API Key** (Access ID): Found in your Tuya IoT project's "Overview" tab.
   - **API Secret** (Access Secret): Also found in the "Overview" tab.
   - **Region**: E.g., `us`, `eu`, `cn`, `in`.
4. It will then fetch your connected devices and create a `devices.json` file in your project folder.
5. Open `devices.json` and find your bulb. Copy its **`ip`**, **`id`** (Device ID), and **`key`** (Local Key).

---

## Step 5: Configure AirLight
1. Open `config.json` in the root of the `Air-Light` folder.
2. Paste your Bulb's IP, Device ID, and Local Key into the file.
3. Set `"mock_mode"` to `false`.

```json
{
  "bulb": {
    "ip": "192.168.1.100",
    "device_id": "YOUR_DEVICE_ID",
    "local_key": "YOUR_LOCAL_KEY",
    "version": 3.3
  },
  "mock_mode": false
}
```

*Note: Most modern Tuya devices use `"version": 3.3` or `"version": 3.4`. Leave it at `3.3` unless you encounter connection errors.*

## You're Done! 🎉
You can now start the application:
```bash
python3 main.py
```
Your gestures will now control the physical bulb instantaneously over your local network!
