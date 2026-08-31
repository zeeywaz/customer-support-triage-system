import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope to read emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Handles OAuth 2.0 authentication and returns the Gmail service."""
    creds = None
    
    # Load existing token if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # Refresh or run interactive login if token is missing or invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def fetch_unread_emails(service, max_results=5):
    """Fetches and parses the latest unread emails."""
    print(f"Fetching up to {max_results} unread emails...")
    results = service.users().messages().list(
        userId='me', 
        labelIds=['UNREAD'], 
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    if not messages:
        print("No unread messages found.")
        return []

    parsed_emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', 
            id=msg['id'], 
            format='full'
        ).execute()
        
        payload = msg_data.get('payload', {})
        headers = payload.get('headers', [])
        
        # Extract Subject
        subject = "No Subject"
        for header in headers:
            if header['name'].lower() == 'subject':
                subject = header['value']
                break
                
        # Extract Body text
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
        elif 'body' in payload:
            data = payload.get('body', {}).get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        parsed_emails.append({
            'id': msg['id'],
            'subject': subject,
            'body': body.strip()
        })
        
    return parsed_emails

if __name__ == '__main__':
    service = authenticate_gmail()
    emails = fetch_unread_emails(service, max_results=5)
    
    for idx, email in enumerate(emails, 1):
        print(f"\n[{idx}] Subject: {email['subject']}")
        print(f"Body snippet: {email['body'][:150]}...")