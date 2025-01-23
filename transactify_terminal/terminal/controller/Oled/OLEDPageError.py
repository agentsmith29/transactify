from django.dispatch import Signal

from .OLEDPage import OLEDPage
import os


class OLEDPageError(OLEDPage):
    name: str = "OLEDPageGenericError"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageError.name: str = str(self.__class__.__name__)

    
    def view(self, error_title, error_message,
             icon=r'/app/static/icons/png_16/x-circle-fill.png', 
             display_back = False,
             next_view = None, *args, **kwargs):
        image, draw = super().view()
        self.ledstrip.animate(self.led_animation)

        header_height = 20
        draw.text((20, 0), error_title, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol

        self.paste_image(image,icon, (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        self.paste_image(image, icon, (0, content_y_start))
        # Wrap the text and draw it
        warped_text = self.wrap_text(error_message, 
                                     self.font_small, 10, 255)
        for line, y in warped_text:
            draw.text((20, content_y_start + y), line, font=self.font_small, fill=(255,255,255))

        # Update the OLED display
        self.send_to_display(image)
        # ------------- Body ----------------
        if next_view:
            self.display_next(image, draw, next_view, 5, *args, **kwargs)
        self.ledstrip.stop_animation()

    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    def on_nfc_read(self, sender, id, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == OLEDPage.BTN_BACK:
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)    
    
    def led_animation(self):
        from rpi_ws281x import Color
        try:
            print('Screensaver animations.')
            while not self.ledstrip.break_loop:
                self.ledstrip.pulse(Color(255, 0, 0), 3)  # Red wipe
            print("Screensaver Animation stopped.")

        except KeyboardInterrupt:
            self.ledstrip.colorWipe(Color(0, 0, 0), 10)
        
        except Exception as e:
            print(f"Error in LEDStripeController: {e}")
            self.ledstrip.colorWipe(Color(0, 0, 0), 10)