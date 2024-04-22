from kivymd.app import MDApp
from kivy_garden.mapview import MapView

class MapViewApp(MDApp):
    def build(self):
        mapview = MapView(zoom=10, lat=51.454514, lon=-2.587910)
        return mapview
    
MapViewApp().run()