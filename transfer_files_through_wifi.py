import os, re
import time
import requests
import platform
import subprocess
from tqdm import tqdm  # Progress bar for file downloads

# Wi-Fi Credentials
WIFI_SSID = "AXILAYER TECH"
WIFI_PASSWORD = "12345678"
ESP32_IP = "http://192.168.4.1"

def connect_to_wifi():
    """Automatically connect the PC to XIAO ESP32S3's Wi-Fi with a password (Windows)."""
    system_platform = platform.system()

    if system_platform == "Windows":
        print("🔄 Connecting to Wi-Fi on Windows...")

        # Create Wi-Fi profile XML content
        profile = f'''<?xml version="1.0"?>
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{WIFI_SSID}</name>
            <SSIDConfig>
                <SSID>
                    <name>{WIFI_SSID}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{WIFI_PASSWORD}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>'''

        # Save profile to a temporary file
        profile_path = os.path.join(os.getcwd(), "wifi_profile.xml")
        with open(profile_path, "w") as f:
            f.write(profile)

        try:
            # Add the Wi-Fi profile
            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}", "user=all"], check=True)

            # Connect using the profile
            subprocess.run(["netsh", "wlan", "connect", f"name={WIFI_SSID}"], check=True)

            print("✅ Connected to Wi-Fi!")

        except subprocess.CalledProcessError:
            print("❌ Failed to connect to Wi-Fi. Make sure the network exists.")

        # Cleanup: Remove the temporary profile file
        os.remove(profile_path)

    elif system_platform == "Linux":
        print("🔄 Connecting to Wi-Fi on Linux...")
        try:
            subprocess.run(["nmcli", "d", "wifi", "connect", WIFI_SSID, "password", WIFI_PASSWORD], check=True)
            print("✅ Connected to Wi-Fi!")
        except subprocess.CalledProcessError:
            print("❌ Failed to connect to Wi-Fi.")

    elif system_platform == "Darwin":  # macOS
        print("🔄 Connecting to Wi-Fi on macOS...")
        try:
            subprocess.run(["networksetup", "-setairportnetwork", "en0", WIFI_SSID, WIFI_PASSWORD], check=True)
            print("✅ Connected to Wi-Fi!")
        except subprocess.CalledProcessError:
            print("❌ Failed to connect to Wi-Fi.")

    else:
        print("❌ Unsupported OS. Please connect manually.")
    time.sleep(5)  # Wait for connection to stabilize

def list_files():
    """Retrieve the list of available files from the ESP32 server."""
    try:
        response = requests.get(f"{ESP32_IP}/")
        if response.status_code == 200:
            print("\n📂 Files available on ESP32:")
            
            # Use regex to extract filenames from <a href='/download?file=FILENAME'>FILENAME</a>
            filenames = re.findall(r"/download\?file=([^']+)'", response.text)

            if filenames:
                for idx, filename in enumerate(filenames, 1):
                    print(f"{idx}. {filename}")
            else:
                print("⚠️ No files found on ESP32 SD card.")

            return filenames
        else:
            print(f"❌ Failed to retrieve file list. HTTP Status Code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error connecting to ESP32: {e}")
        return []

def download_file(filename):
    """Download a file from the ESP32 server with a progress bar."""
    url = f"{ESP32_IP}/download?file={filename}"
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))
            print(f"\n⬇️ Downloading {filename} ({total_size / 1024:.2f} KB)...")

            with open(filename, "wb") as file, tqdm(
                desc=filename,
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        bar.update(len(chunk))
            print(f"✅ Download complete: {filename}")
        else:
            print(f"❌ Failed to download {filename}, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error downloading file: {e}")

def delete_file(filename):
    """Delete a file from the ESP32 server."""
    url = f"{ESP32_IP}/delete?file={filename}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"🗑️ File deleted: {filename}")
        else:
            print(f"❌ Failed to delete {filename}, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error deleting file: {e}")

if __name__ == "__main__":
    print("\n🔄 Connecting to XIAO ESP32S3 Wi-Fi...")
    connect_to_wifi()
    
    print("\n📋 Listing files from ESP32S3 SD card...\n")
    files = list_files()

    if files:
        print("\nChoose an action:")
        print("1️⃣ Download files")
        print("2️⃣ Delete files")
        action = input("> ")

        if action == "1":
            print("\n✏️ Enter the file numbers you want to download (comma-separated, e.g., 1,3,5) or type 'all' to download everything.")
            selection = input("> ")

            if selection.lower() == "all":
                selected_files = files  # Download all files
            else:
                try:
                    indices = [int(i.strip()) - 1 for i in selection.split(",")]
                    selected_files = [files[i] for i in indices if 0 <= i < len(files)]
                except ValueError:
                    print("❌ Invalid input. Exiting.")
                    exit()

            if selected_files:
                for file in selected_files:
                    download_file(file)
            else:
                print("⚠️ No valid files selected. Exiting.")

        elif action == "2":
            print("\n✏️ Enter the file numbers you want to delete (comma-separated, e.g., 1,3,5).")
            selection = input("> ")

            try:
                indices = [int(i.strip()) - 1 for i in selection.split(",")]
                selected_files = [files[i] for i in indices if 0 <= i < len(files)]
            except ValueError:
                print("❌ Invalid input. Exiting.")
                exit()

            for file in selected_files:
                delete_file(file)

        else:
            print("❌ Invalid option. Exiting.")
