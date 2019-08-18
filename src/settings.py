from gi.repository import Gio

class TelexSettings(Gio.Settings):
    def __init__(self):
        super().__init__()

    def new():
        settings = Gio.Settings.new("com.rafaelmardojai.Telex")
        settings.__class__ = TelexSettings
        return settings

