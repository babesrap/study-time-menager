import json
import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarAdapter:
    def __init__(self):
        self.creds = self.get_credentials()
        if self.creds:
            self.service = build("calendar", "v3", credentials=self.creds)
        else:
            print("Uwaga: Brak ważnych poświadczeń. Ustaw tokeny dostępu w token.json lub uruchom autoryzację.")

    def get_credentials(self):
        """Uzyskaj poświadczenia do Google Calendar API"""
        creds = None
        
        # Sprawdź czy plik token.json istnieje i czy zawiera prawdziwe tokeny
        if os.path.exists("token.json"):
            try:
                with open("token.json", "r") as f:
                    token_data = json.load(f)
                
                # Sprawdź, czy token nie jest placeholderem
                if (token_data.get("token") != "YOUR_ACCESS_TOKEN_HERE" and 
                    token_data.get("client_id") != "YOUR_CLIENT_ID_HERE"):
                    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            except (json.JSONDecodeError, KeyError):
                print("Błąd w pliku token.json")
        
        # Jeśli brak ważnych tokenów lub token wygasł, przeprowadź autoryzację
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Nie można odświeżyć tokenu: {e}")
                    return self.run_authorization_flow()
            else:
                return self.run_authorization_flow()
                
            # Zapisz nowe tokeny
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                
        return creds
    
    def run_authorization_flow(self):
        """Uruchamia pełny proces autoryzacji"""
        try:
            if os.path.exists("credentials.json"):
                with open("credentials.json", "r") as f:
                    cred_data = json.load(f)
                
                # Sprawdź czy dane uwierzytelniające nie są placeholderami
                if (cred_data.get("installed", {}).get("client_id") != "YOUR_CLIENT_ID_HERE"):
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                    return flow.run_local_server(port=0)
                else:
                    print("Plik credentials.json zawiera placeholdery. Uzupełnij prawdziwe dane.")
                    return None
            else:
                print("Brak pliku credentials.json. Utwórz projekt w Google Cloud Console i pobierz plik uwierzytelniający.")
                return None
        except Exception as e:
            print(f"Błąd podczas autoryzacji: {e}")
            return None

    def add_event(self, title, date):
        if not hasattr(self, 'service'):
            print("Brak połączenia z Google Calendar API. Ustaw poprawne tokeny.")
            return False
            
        event = {
            "summary": title,
            "start": {"date": date},  
            "end": {"date": date}
        }

        print(f"Dodawanie wydarzenia do kalendarza: {title} na {date}")

        try:
            self.service.events().insert(calendarId="primary", body=event).execute()
            print("Wydarzenie dodane pomyślnie!")
            return True
        except Exception as e:
            print(f"Błąd przy dodawaniu wydarzenia: {e}")
            return False
