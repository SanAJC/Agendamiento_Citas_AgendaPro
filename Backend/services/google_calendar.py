from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from allauth.socialaccount.models import SocialToken, SocialAccount
import datetime
#Google Calendar
class GoogleCalendarService:
    @staticmethod
    def get_credentials(user):
        try:
            social_account = SocialAccount.objects.get(user=user, provider='google')
            social_token = SocialToken.objects.get(account=social_account)
            
            # Verificar si tenemos el refresh_token
            if not social_token.token_secret:
                print(f"Error: No se encontró refresh_token para el usuario {user.username}")
                return None
                
            credentials = Credentials(
                token=social_token.token,
                refresh_token=social_token.token_secret,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            return credentials
        except (SocialAccount.DoesNotExist, SocialToken.DoesNotExist) as e:
            print(f"Error al obtener credenciales para Google Calendar: {e}")
            return None
    
    @staticmethod
    def create_calendar_event(user, appointment):
        credentials = GoogleCalendarService.get_credentials(user)
        if not credentials:
            return None
        
        service = build('calendar', 'v3', credentials=credentials)
        
        start_datetime = datetime.datetime.combine(appointment.date, appointment.time)
        end_datetime = datetime.datetime.combine(appointment.date, appointment.time)
        
        # Crear evento
        event = {
            'summary': f'Cita con {appointment.customer.username}',
            'description': f'Reservación ID: {appointment.id}',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        try:
            event = service.events().insert(calendarId='primary', body=event).execute()
            return event.get('id')
        except Exception as e:
            print(f"Error al crear evento en Google Calendar: {e}")
            return None
    
    @staticmethod
    def update_calendar_event(user, appointment, event_id):
        credentials = GoogleCalendarService.get_credentials(user)
        if not credentials:
            return False
        
        service = build('calendar', 'v3', credentials=credentials)
        
        
        start_datetime = datetime.datetime.combine(appointment.date, appointment.time)
        end_datetime = datetime.datetime.combine(appointment.date, appointment.time)
        
        # Obtener evento existente
        try:
            event = service.events().get(calendarId='primary', eventId=event_id).execute()

            event['summary'] = f'Cita con {appointment.customer.username}'
            event['description'] = f'Reservación ID: {appointment.id}'
            event['start'] = {
                'dateTime': start_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            }
            event['end'] = {
                'dateTime': end_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            }
            
            updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            return True
        except Exception as e:
            print(f"Error al actualizar evento en Google Calendar: {e}")
            return False
    
    @staticmethod
    def delete_calendar_event(user, appointment, event_id):
        credentials = GoogleCalendarService.get_credentials(user)
        if not credentials:
            return False
        
        service = build('calendar', 'v3', credentials=credentials)
        
        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except Exception as e:
            print(f"Error al eliminar evento en Google Calendar: {e}")
            return False