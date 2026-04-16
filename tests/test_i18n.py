import unittest
from utils.i18n import get_text, set_language

class TestI18n(unittest.TestCase):
    def test_get_text_existing(self):
        set_language("de")
        self.assertEqual(get_text("main_menu"), "Hauptmenü")
    
    def test_get_text_non_existing(self):
        self.assertEqual(get_text("non_existing_key"), "non_existing_key")
        
    def test_get_text_formatting(self):
        set_language("de")
        # "device_connected": "Aktuelles Gerät: {serial}"
        text = get_text("device_connected", serial="XYZ")
        self.assertEqual(text, "Aktuelles Gerät: XYZ")

if __name__ == '__main__':
    unittest.main()
