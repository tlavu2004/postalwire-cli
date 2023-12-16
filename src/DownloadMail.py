import email
from email import policy
from email.parser import BytesParser

# Parse the email content
msg = BytesParser(policy=policy.default).parsebytes(email_content.encode('utf-8'))

# Extract information from the parsed email
print(f"From: {msg.get('From')}")
print(f"To: {msg.get('To')}")
print(f"CC: {msg.get('CC')}")
print(f"BCC: {msg.get('BCC')}")
print(f"Subject: {msg.get('Subject')}")

# If the email is multipart, parse its parts
if msg.is_multipart():
    for part in msg.iter_parts():
        content_type = part.get_content_type()
        print(f"\nContent-Type: {content_type}")
        
        # For text/plain parts, print the content
        if 'text/plain' in content_type:
            print(part.get_payload())
else:
    # For non-multipart emails, print the content directly
    print(f"\nContent-Type: {msg.get_content_type()}")
    print(msg.get_payload())
