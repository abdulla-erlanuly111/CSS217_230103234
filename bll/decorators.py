from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, message: str) -> str:
        pass

class BasicConsoleNotifier(Notifier):
    def send(self, message: str) -> str:
        log_msg = f"[CONSOLE LOG] {message}"
        print(log_msg)
        return log_msg

class BaseNotifierDecorator(Notifier):
    def __init__(self, wrapped_notifier: Notifier):
        self._wrapped_notifier = wrapped_notifier

    def send(self, message: str) -> str:
        return self._wrapped_notifier.send(message)

class SmsNotificationDecorator(BaseNotifierDecorator):
    def send(self, message: str) -> str:
        result = super().send(message)
        sms_msg = f"[SMS ALERT SENT] {message}"
        print(sms_msg)
        return f"{result} | {sms_msg}"

class EmailNotificationDecorator(BaseNotifierDecorator):
    def send(self, message: str) -> str:
        result = super().send(message)
        email_msg = f"[EMAIL ALERT SENT] {message}"
        print(email_msg)
        return f"{result} | {email_msg}"

class HighPriorityAlertDecorator(BaseNotifierDecorator):
    def send(self, message: str) -> str:
        urgent_message = f"🚨 HIGH PRIORITY OVERBUDGET: {message}"
        return super().send(urgent_message)
