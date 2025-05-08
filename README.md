# SMS Forward

This is a simple script that uses the [Termux API](https://wiki.termux.com/wiki/Termux:API) to forward new SMS messages from your Android phone to an email address.

Instead of forwarding SMS messages directly via SMS, this script sends them over email. This is a personal decision based on my situation, where:

* My phone can still receive SMS for free
* Sending SMS is expensive
* I have Wi-Fi or mobile data available

---

## Prerequisites

Make sure the following Termux components are installed and properly configured on your Android device. Additionally, grant Termux:API the necessary permissions for Contacts and SMS.

* [Termux](https://wiki.termux.com/wiki/Installation)
* [Termux\:API](https://wiki.termux.com/wiki/Termux:API)
* [Termux\:Boot](https://wiki.termux.com/wiki/Termux:Boot)

All setup steps below should be executed inside the Termux terminal.

---

## Setup Instructions

### 1. Clone the Repository

If Git is not installed:

```bash
apt update
apt install git
```

Then, clone this repository:

```bash
cd ~
git clone https://github.com/Rockruff/SMS-Forward.git
```

### 2. Configure SMTP Settings

Navigate to the project folder and edit the configuration file:

```bash
cd ~/SMS-Forward
nano config.smtp.json  # Or use any text editor
```

Fill in the SMTP settings. Example (using Gmail):

```json
{
  "server": "smtp.gmail.com",
  "port": 465,
  "sender": "someone@gmail.com",
  "password": "0123456789abcdef",
  "recipient": "someone@icloud.com"
}
```

**Field explanations:**

* **`server`**: SMTP server address (e.g., `smtp.gmail.com` for Gmail)
* **`port`**: SMTP port (use `465` for SSL)
* **`sender`**: Email address used to send the forwarded SMS
* **`password`**: Password for the sender account. Gmail users must use an [app-specific password](https://myaccount.google.com/apppasswords)
* **`recipient`**: Email address to receive the forwarded SMS messages

### 3. Test the Script

If Python is not installed:

```bash
apt install python3
```

Run the script:

```bash
python3 main.py
```

The script will only forward **new** SMS messages received after it starts. Messages that are already in your inbox will not be forwarded. You might want to send a test SMS to your phone to confirm everything is working.

---

## Auto-Start on Boot

To make the script run automatically at boot using Termux\:Boot:

1. Create the `boot` directory if it doesn't exist:

   ```bash
   mkdir -p ~/.termux/boot
   ```

2. Create and edit a startup script:

   ```bash
   cd ~/.termux/boot
   nano start-sms-forward
   ```

3. Add the following contents to the script:

   ```bash
   #!/data/data/com.termux/files/usr/bin/sh
   termux-wake-lock
   nohup bash -c 'cd ~/SMS-Forward && python3 main.py' &
   ```

4. Make the script executable:

   ```bash
   chmod +x start-sms-forward
   ```

---

## Final Step: Reboot and Verify

Reboot your phone. The script should start automatically and forward any new incoming SMS via email.

You may need to unlock your phone to see the script's notifications.
