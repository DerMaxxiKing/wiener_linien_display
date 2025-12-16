import os
import time
import crowpanel

panel = crowpanel.CrowPanel42()

#power led
panel.led.on()

#e-ink display
display = panel.get_display()


from writer import Writer
import freesans20
import courier20

#work with framebuffer
display.fill(1)

display.large_text('HUGE', 0, 0, 4, 0)

wri = Writer(display, courier20)
Writer.set_textpos(display, 200, 0)  # verbose = False to suppress console output
wri.printstring('Sunday\n', invert=True)
wri.printstring('12 Aug 2018 gzj\n', invert=True)
wri.printstring('10.30am', invert=True)
display.show()


try:
    #mount sd card
    panel.mount_sdcard('/sd')
except Exception as e:
    display.text('No sd card', 0, 12, 0)
else:
    display.text('Files on sd card:', 0, 12, 0)
    y = 22
    for i,item in enumerate(os.listdir('/sd')):
        display.text('-' + item, 8, y + i * 10, 0)
        
display.text('xdhrh', 8, 50, 0)

display.large_text('HUGE', 0, 32, 4, 1)
        
        
display.line(50, 50, 80, 80, 0)
display.ellipse(130,170, 50, 50, 0, True, 3)


display.show()

#go to deep sleep
display.sleep()

