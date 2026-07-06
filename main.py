import sys
import cv2
import time
from core import AirLightCore
from logger import logger

def main():
    logger.info("Starting AirLight Native OpenCV UI...")
    
    core = AirLightCore()
    core.start()
    
    # Create the OpenCV window
    cv2.namedWindow("AirLight - AI Smart Lighting", cv2.WINDOW_NORMAL)
    
    try:
        while True:
            core.ping_heartbeat()
            
            if core.current_frame is not None:
                # Copy frame to draw text over it
                frame = core.current_frame.copy()
                
                # Fetch live status from core
                status = core.get_status()
                
                # --- CYBERPUNK HUD OVERLAY ---
                h, w = frame.shape[:2]
                
                # 2. Side Panel (Semi-transparent)
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (320, h), (15, 15, 15), -1)
                cv2.rectangle(overlay, (w - 150, 0), (w, 50), (15, 15, 15), -1)
                cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
                
                # 3. HUD Border Brackets (Acid Green)
                b_color = (0, 255, 100) # Acid Green in BGR
                thick = 2
                leng = 40
                gap = 20
                # Top-Left
                cv2.line(frame, (gap, gap), (gap+leng, gap), b_color, thick)
                cv2.line(frame, (gap, gap), (gap, gap+leng), b_color, thick)
                # Bottom-Left
                cv2.line(frame, (gap, h-gap), (gap+leng, h-gap), b_color, thick)
                cv2.line(frame, (gap, h-gap), (gap, h-gap-leng), b_color, thick)
                # Top-Right
                cv2.line(frame, (w-gap, gap), (w-gap-leng, gap), b_color, thick)
                cv2.line(frame, (w-gap, gap), (w-gap, gap+leng), b_color, thick)
                # Bottom-Right
                cv2.line(frame, (w-gap, h-gap), (w-gap-leng, h-gap), b_color, thick)
                cv2.line(frame, (w-gap, h-gap), (w-gap, h-gap-leng), b_color, thick)

                # 4. Text Data (Tech style)
                font = cv2.FONT_HERSHEY_DUPLEX
                accent_color = (0, 255, 100)
                white = (245, 245, 245)
                
                # Title
                cv2.putText(frame, "AIRLIGHT OS", (30, 50), font, 0.9, white, 1, cv2.LINE_AA)
                cv2.line(frame, (30, 65), (280, 65), accent_color, 2)
                
                # Status Texts
                y_offset = 110
                dy = 40
                
                labels = [
                    ("LUMA_LVL", f"{status.get('brightness', 0)}%"),
                    ("CHROMA", f"{status.get('saturation', 0)}%"),
                    ("SPECTRUM", f"{status.get('color', 'White')}"),
                    ("PWR_STATE", f"{status.get('power', 'OFF')}"),
                ]
                
                # Gesture display (Highlighted)
                g_text = status.get('gesture', 'None')
                cv2.putText(frame, "ACTIVE_SIG:", (30, y_offset), font, 0.6, white, 1)
                cv2.putText(frame, g_text.upper(), (30, y_offset + 30), font, 1.1, accent_color if g_text != "None" else (100, 100, 100), 2)
                y_offset += 80
                
                for label, val in labels:
                    cv2.putText(frame, label, (30, y_offset), font, 0.6, white, 1)
                    cv2.putText(frame, val, (180, y_offset), font, 0.7, accent_color, 1)
                    y_offset += dy
                    
                # FPS / Status Top Right
                fps = status.get('fps', '0')
                cv2.putText(frame, f"FPS: {fps}", (w - 130, 32), font, 0.8, accent_color, 1)
                
                # Rec Blinker
                if int(time.time() * 2) % 2 == 0:
                    cv2.circle(frame, (w - 30, h - 30), 8, (0, 0, 255), -1)
                cv2.putText(frame, "REC", (w - 80, h - 25), font, 0.8, (0, 0, 255), 1)
                
                # Show the blazing fast OpenCV popup
                cv2.imshow("AirLight - AI Smart Lighting", frame)
                
            # Press 'q' or ESC to quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
                
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}", exc_info=True)
    finally:
        logger.info("Exiting...")
        core.stop()
        cv2.destroyAllWindows()
        sys.exit(0)

if __name__ == "__main__":
    main()
