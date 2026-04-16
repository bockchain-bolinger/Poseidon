import functools
from utils.i18n import get_text
from utils.ui_helpers import wait_for_enter

def require_device(func):
    """
    Decorator, der prüft, ob ein Gerät im DeviceManager ausgewählt ist.
    Falls nicht, wird eine Fehlermeldung ausgegeben und die Funktion abgebrochen.
    """
    @functools.wraps(func)
    def wrapper(device_manager, adb, *args, **kwargs):
        serial = device_manager.get_current_device()
        if not serial:
            print(get_text("no_device"))
            wait_for_enter()
            return None
        return func(device_manager, adb, *args, **kwargs)
    return wrapper
