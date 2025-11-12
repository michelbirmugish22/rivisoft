from django.core.mail import send_mail
class envoyer_mail:
    def __init__(self, sujet, message, email_expeditaire, emaix_destinataire):
        try:
            send_mail(
                subject=sujet,
                message=message,
                from_email=email_expeditaire,
                recipient_list=[emaix_destinataire],
                fail_silently=False
            )
        except Exception as e:
            return e
    
    
        
