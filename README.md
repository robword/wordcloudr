# WordCloud App Setup

## Prerequisites

- Ubuntu 24.04.2 LTS (or compatible)
- User with `sudo` privileges
- Internet connection

## Setup Instructions

1. **Download and run the setup script:**

   Replace `<RAW_SCRIPT_URL>` with the direct URL to your `setup_wordcloud_app.sh` file (for example, from GitHub raw):

   ```bash
   curl -fsSL <RAW_SCRIPT_URL> | bash
   ```

   The script will:
   - Update and upgrade system packages
   - Install required dependencies
   - Set up a Python virtual environment
   - Install Python packages
   - Download the spaCy English model
   - Download your app source code
   - Set up and start a systemd service for the app

2. **Check the service status:**

   ```bash
   sudo systemctl status wordcloud.service
   ```

3. **Access the app:**  
   Open your browser to the address/port where your app is running (see your app's documentation for details).  
   If running in the dev container, you can use:

   ```bash
   "$BROWSER" http://localhost:<port>
   ```

---

**Note:**  
If running in a dev container, you may need to adjust paths or permissions as appropriate for your setup.
