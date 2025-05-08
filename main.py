import json
import smtplib
import socket
import subprocess
import time
import traceback
from email.mime.text import MIMEText
from io import StringIO


# Runs a shell command and returns its UTF-8 decoded output
def run_command(*command) -> str:
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    return result.stdout


# Prints messages to a file-like object (e.g., StringIO)
def file_print(file, *args, **kwargs) -> None:
    print(*args, file=file, **kwargs)


# Sends an email with the given subject and plain text content
def send_email(subject: str, content: str) -> None:
    # Load SMTP configuration from a JSON file
    with open("config.smtp.json") as f:
        config = json.load(f)

    # Extract SMTP and recipient information
    server = config["server"]
    port = config["port"]
    sender = config["sender"]
    password = config["password"]
    recipient = config["recipient"]

    # Compose the plain text email message
    msg = MIMEText(content, "plain")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    # Send the email using SMTP over SSL
    with smtplib.SMTP_SSL(server, port) as server:
        server.login(sender, password)
        server.send_message(msg)


# Lists SMS messages from Termux inbox that have IDs greater than the given offset
def list_messages(offset: int):
    # Run termux command and parse JSON output
    result = run_command('termux-sms-list', '-t', 'inbox')
    messages = json.loads(result)

    # Filter messages based on the offset
    new_messages = [msg for msg in messages if msg["_id"] > offset]
    new_offset = offset

    # Update the offset to the latest message ID
    if new_messages:
        new_messages.sort(key=lambda msg: msg["_id"])
        new_offset = new_messages[-1]["_id"]

    return new_messages, new_offset


# Sends an email notification summarizing the list of new SMS messages
def forward_sms_via_email(messages: list[dict]) -> None:
    if not messages:
        return

    buffer = StringIO()

    for i, msg in enumerate(messages):
        # Separate messages with a delimiter
        if i > 0:
            file_print(buffer, '--------------------')
            file_print(buffer)
        # Format and print message details to buffer
        file_print(buffer, "Time:", msg["received"])
        file_print(buffer, "From:", msg["number"])
        file_print(buffer)
        file_print(buffer, msg["body"])
        file_print(buffer)

    # Send the formatted messages via email
    send_email("SMS Forward", buffer.getvalue())


def main() -> None:
    # Interval for checking new messages
    SLEEP_INTERVAL = 45

    # Notification IDs for Termux
    # These IDs ensure that new notifications of the same type replace older ones
    NID_ACTIVITY = '0'
    NID_EMAIL_ERROR = '1'
    NID_UNEXPECTED_ERROR = '2'

    # Start from the beginning of the inbox
    offset = 0

    # Try to skip any existing messages already in the inbox at startup
    try:
        messages, offset = list_messages(offset)
    except:
        pass

    # Main loop to poll new messages and forward them via email
    while True:
        try:
            # Wait before polling again
            time.sleep(SLEEP_INTERVAL)

            # Show activity notification
            timestamp = time.strftime("%Y-%m-%d %H:%M")
            run_command(
                "termux-notification",
                "--id", NID_ACTIVITY,
                "--priority", "low",
                "--title", "SMS Forward - Running",
                "--content", f"Last seen: {timestamp}"
            )

            # Get and forward new messages
            messages, new_offset = list_messages(offset)
            forward_sms_via_email(messages)
            offset = new_offset

        except (smtplib.SMTPException, socket.error) as e:
            # Show email error notification
            error_msg = str(e) + '\n' + traceback.format_exc()
            run_command(
                "termux-notification",
                "--id", NID_EMAIL_ERROR,
                "--priority", "high",
                "--title", "SMS Forward - Email Sending Error",
                "--content", error_msg
            )

        except Exception as e:
            # Show unexpected error notification
            error_msg = str(e) + '\n' + traceback.format_exc()
            run_command(
                "termux-notification",
                "--id", NID_UNEXPECTED_ERROR,
                "--priority", "max",
                "--title", "SMS Forward - Unexpected Error",
                "--content", error_msg
            )


if __name__ == "__main__":
    main()
