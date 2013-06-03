"""
vispy backend for glut.
"""

from __future__ import print_function, division, absolute_import

from vispy.event import Event
from vispy import app
from vispy import keys
import vispy.util.ptime as ptime
import vispy

import OpenGL.GLUT as glut


# glut.GLUT_ACTIVE_SHIFT: keys.SHIFT,
# glut.GLUT_ACTIVE_CTRL: keys.CONTROL,
# glut.GLUT_ACTIVE_ALT: keys.ALT,
# -1: keys.META,
    
# Map native keys to vispy keys
KEYMAP = {
    -1: keys.SHIFT,
    -2: keys.CONTROL,
    -3: keys.ALT,
    -4: keys.META,
    
    glut.GLUT_KEY_LEFT: keys.LEFT,
    glut.GLUT_KEY_UP: keys.UP,
    glut.GLUT_KEY_RIGHT: keys.RIGHT,
    glut.GLUT_KEY_DOWN: keys.DOWN,
    glut.GLUT_KEY_PAGE_UP: keys.PAGEUP,
    glut.GLUT_KEY_PAGE_DOWN: keys.PAGEDOWN,
    
    glut.GLUT_KEY_INSERT: keys.INSERT,
    chr(127): keys.DELETE,
    glut.GLUT_KEY_HOME: keys.HOME,
    glut.GLUT_KEY_END: keys.END,
    
    chr(27): keys.ESCAPE,
    chr(8): keys.BACKSPACE,
    
    glut.GLUT_KEY_F1: keys.F1,
    glut.GLUT_KEY_F2: keys.F2,
    glut.GLUT_KEY_F3: keys.F3,
    glut.GLUT_KEY_F4: keys.F4,
    glut.GLUT_KEY_F5: keys.F5,
    glut.GLUT_KEY_F6: keys.F6,
    glut.GLUT_KEY_F7: keys.F7,
    glut.GLUT_KEY_F8: keys.F8,
    glut.GLUT_KEY_F9: keys.F9,
    glut.GLUT_KEY_F10: keys.F10,
    glut.GLUT_KEY_F11: keys.F11,
    glut.GLUT_KEY_F12: keys.F12,
    
    ' ': keys.SPACE,
    '\r': keys.ENTER,
    '\n': keys.ENTER,
    '\t': keys.TAB,
}

ALL_WINDOWS = []

class ApplicationBackend(app.ApplicationBackend):
    def __init__(self):
        app.ApplicationBackend.__init__(self)
        self._inizialized = False
        self._windows = []
        
    
    def _vispy_get_backend_name(self):
        return 'Glut'
    
    def _vispy_process_events(self):
        pass # not possible?
    
    def _vispy_run(self):
        self._vispy_get_native_app() # Force exist
        return glut.glutMainLoop()
    
    def _vispy_quit(self):
        global ALL_WINDOWS
        for win in ALL_WINDOWS:
            win._vispy_close()
    
    def _vispy_get_native_app(self):
        if not self._inizialized:
            glut.glutInit() # todo: maybe allow user to give args?
            self._inizialized = True
        return glut



class CanvasBackend(app.CanvasBackend):
    """ GLUT backend for Canvas abstract class."""
    
    def __init__(self, name='glut window', *args, **kwargs):
        app.CanvasBackend.__init__(self)
        self._id = glut.glutCreateWindow(name)
        global ALL_WINDOWS
        ALL_WINDOWS.append(self)
        
        # Note: this seems to cause the canvas to ignore calls to show()
        # about half of the time. 
        #glut.glutHideWindow()  # Start hidden, like the other backends
        
        # Register callbacks
        glut.glutDisplayFunc(self.on_draw)
        glut.glutReshapeFunc(self.on_resize)
        #glut.glutVisibilityFunc(self.on_show)
        glut.glutKeyboardFunc(self.on_key_press)
        glut.glutSpecialFunc(self.on_key_press)
        glut.glutKeyboardUpFunc(self.on_key_release)
        glut.glutMouseFunc(self.on_mouse_action)
        glut.glutMotionFunc(self.on_mouse_motion)
        glut.glutCloseFunc(self.on_close)
        #glut.glutFunc(self.on_)
        
        self._initialized = False
        
        # LC: I think initializing here makes it more consistent with other backends
        glut.glutTimerFunc(0, self._emit_initialize, None)
        
    def _emit_initialize(self, _):
        self._initialized = True
        self._vispy_canvas.events.initialize()
        
    def _vispy_set_current(self):  
        # Make this the current context
        glut.glutSetWindow(self._id)
    
    def _vispy_swap_buffers(self):  
        # Swap front and back buffer
        glut.glutSetWindow(self._id)
        glut.glutSwapBuffers()
    
    def _vispy_set_title(self, title):  
        # Set the window title. Has no effect for widgets
        glut.glutSetWindow(self._id)
        glut.glutSetWindowTitle(title)
    
    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        glut.glutSetWindow(self._id)
        glut.glutReshapeWindow(w, h)
    
    def _vispy_set_location(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        glut.glutSetWindow(self._id)
        glut.glutPositionWindow(x, y)
    
    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        glut.glutSetWindow(self._id)
        if visible:
            glut.glutShowWindow()
        else:
            glut.glutHideWindow()
    
    def _vispy_update(self):
        # Invoke a redraw
        glut.glutSetWindow(self._id)
        glut.glutPostRedisplay()
    
    def _vispy_close(self):
        # Force the window or widget to shut down
        glut.glutDestroyWindow(self._id)
    
    def _vispy_get_geometry(self):
        # Should return widget (x, y, w, h)
        glut.glutSetWindow(self._id)
        x = glut.glutGet(glut.GLUT_WINDOW_X)
        y = glut.glutGet(glut.GLUT_WINDOW_Y)
        w = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        h = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        return x, y, w, h
    
    
    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w,h))
    
    def on_close(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.close()
    
    def on_draw(self, dummy=None):
        if self._vispy_canvas is None:
            return
        if not self._initialized:
            raise Exception('this should not happen')
        # Initialize?
        #if not self._initialized:
            #self._initialized = True
            #self._vispy_canvas.events.initialize()
        
        #w = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        #h = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        self._vispy_canvas.events.paint(region=None)  #(0, 0, w, h))
    
    def on_mouse_action(self, button, state, x, y):
        if self._vispy_canvas is None:
            return
        action = {glut.GLUT_UP:'release', glut.GLUT_DOWN:'press'}[state]
        mod = self._modifiers()
        
        if button < 3:
            # Mouse click event
            button = {glut.GLUT_LEFT_BUTTON:0, glut.GLUT_RIGHT_BUTTON:1}.get(button, button)
            if action == 'press':
                self._vispy_canvas.events.mouse_press(pos=(x,y), button=button, modifiers=mod)
            else:
                self._vispy_canvas.events.mouse_release(pos=(x,y), button=button, modifiers=mod)
        
        elif button in (3, 4):
            # Wheel event
            self._vispy_canvas.events.mouse_wheel(
                pos=(x, y),
                delta=(120 if button==3 else -120),  # Follow Qt stepsize
                modifiers=mod,
                )
    
    def on_mouse_motion(self, x, y):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_move(
            pos=(x, y),
            button=None,  # todo: self._buttons_pressed,
            modifiers=self._modifiers(),
            )
    
    
    def on_key_press(self, key, x, y):
        key, text = self._process_key(key)
        self._vispy_canvas.events.key_press(
                key=key, 
                text=text,
                modifiers=self._modifiers(),
            )
    
    def on_key_release(self, key, x, y):
        key, text = self._process_key(key)
        self._vispy_canvas.events.key_release(
                key=key, 
                text=text,
                modifiers=self._modifiers()
            )

    def _process_key(self, key):
        if key in KEYMAP:
            if isinstance(key, int):
                return KEYMAP[key], ''
            else:
                return KEYMAP[key], key
        elif isinstance(key, int):
            return None, '' # unsupported special char
        else:
            return keys.Key(key.upper()), key
    
    def _modifiers(self):
        glutmod = glut.glutGetModifiers()
        mod = ()
        if glut.GLUT_ACTIVE_SHIFT & glutmod:
            mod += keys.SHIFT,
        if glut.GLUT_ACTIVE_CTRL & glutmod:
            mod += keys.CONTROL,
        if glut.GLUT_ACTIVE_ALT & glutmod:
            mod += keys.ALT,
        return mod


import weakref

def _glut_callback(id):
    # Get weakref wrapper for timer
    timer = TimerBackend._timers.get(id, None)
    if timer is None:
        return
    # Get timer object
    timer = timer()
    if timer is None:
        return
    # Kick it!
    if timer._vispy_timer._running:
        timer._vispy_timer._timeout()
        ms = int(timer._vispy_timer._interval*1000)
        glut.glutTimerFunc(ms, _glut_callback, timer._id)


#class TimerBackend(app.TimerBackend):
    #_counter = 0
    #_timers = {}
    
    #def __init__(self, vispy_timer):
        #app.TimerBackend.__init__(self, vispy_timer)
        ## Give this timer a unique id
        #TimerBackend._counter += 1
        #self._id = TimerBackend._counter
        ## Store this timer (using a weak ref)
        #self._timers[self._id] = weakref.ref(self)
    
    #@classmethod
    #def _glut_callback(cls, id):
        ## Get weakref wrapper for timer
        #timer = cls._timers.get(id, None)
        #if timer is None:
            #return
        ## Get timer object
        #timer = timer()
        #if timer is None:
            #return
        ## Kick it!
        #if timer._vispy_timer._running:
            #timer._vispy_timer._timeout()
            #ms = int(timer._vispy_timer._interval*1000)
            #glut.glutTimerFunc(ms, TimerBackend._glut_callback, timer._id)
    
    #def _vispy_start(self, interval):
        ##glut.glutTimerFunc(int(interval*1000), TimerBackend._glut_callback, self._id)
        #glut.glutTimerFunc(int(interval*1000), _glut_callback, self._id)
    
    #def _vispy_stop(self):
        #pass
    
    #def _vispy_get_native_timer(self):
        #return glut # or self?

# Note: we could also build a timer using glutTimerFunc, but this causes trouble
# because timer callbacks appear to take precedence over all others. Thus,
# a fast timer can block new display events.
class TimerBackend(app.TimerBackend):
    _initialized = False
    _schedule = []
    
    def __init__(self, vispy_timer):
        app.TimerBackend.__init__(self, vispy_timer)
        self._init_class()

    @classmethod
    def _init_class(cls):
        if cls._initialized:
            return
        glut.glutIdleFunc(cls._idle_callback)
        cls._initialized = True
    
    @classmethod
    def _idle_callback(cls):
        now = ptime.time()
        new_schedule = []
        
        ## see whether there are any timers ready
        while len(cls._schedule) > 0 and cls._schedule[0][0] <= now:
            timer = cls._schedule.pop(0)[1]
            timer._vispy_timer._timeout()
            if timer._vispy_timer.running:
                new_schedule.append((now+timer._vispy_timer.interval, timer))
                
        ## schedule next round of timeouts
        if len(new_schedule) > 0:
            cls._schedule.extend(new_schedule)    
            cls._schedule.sort()
                
    def _vispy_start(self, interval):
        now = ptime.time()
        self._schedule.append((now + interval, self))
    
    def _vispy_stop(self):
        pass
    
    def _vispy_get_native_timer(self):
        return None  # glut has no native timer objects.