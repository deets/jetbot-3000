import Tkinter


class GuiMotorControl(object):


    def __init__(self):
        pass


    def __call__(self):
        # this just fulfills the motor_control_class
        # protocol
        return self


    def control(self, command):
        if self._drive_sym is not None:
            self._canvas.delete(self._drive_sym)
            self._drive_sym = None

        coords = dict(
            forward=(20, 40, 30, 20, 40, 40),
            spin_left=(20, 40, 30, 20, 30, 60),
            spin_right=(30, 20, 40, 40, 30, 60),
            stop=(20, 40, 30, 20, 40, 40, 30, 60),
            reverse=(20, 40, 30, 60, 40, 40),
            shutdown=(),
            )[command]

        if coords:
            self._drive_sym = self._canvas.create_polygon(
                *coords
                )


    def start(self):
        self._tk = Tkinter.Tk()
        frame = Tkinter.Frame(self._tk, relief=Tkinter.RIDGE, borderwidth=2)
        frame.pack(fill=Tkinter.BOTH,expand=1)
        canvas = Tkinter.Canvas(frame, width=100, height=100)
        canvas.pack(fill=Tkinter.X, expand=1)
        button = Tkinter.Button(frame,text="Exit", command=self._tk.destroy)
        button.pack(side=Tkinter.BOTTOM)

        self._canvas = canvas
        self._drive_sym = canvas.create_rectangle(10, 20, 30, 40)


    def scheduler(self, hub):

        def timercallback():
            hub.process_once()
            self._tk.after(100, timercallback)

        self._tk.after(100, timercallback)
        hub.start()
        self._tk.mainloop()
