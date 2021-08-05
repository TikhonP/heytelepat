"""
LED light pattern like Google Home
"""
import asyncio
import logging
import threading
from queue import Queue

try:
    from core import apa102
except ImportError:
    logging.warning("Pixels unavailable spi_dev error")
    apa102 = None


class Pixels:
    PIXELS_N = 3

    def __init__(self, loop, development=False):
        self.development = development
        if development:
            logging.info("Pixels in development mode")
            return

        self.basis = [0] * 3 * self.PIXELS_N
        self.basis[0] = 2
        self.basis[3] = 1
        self.basis[4] = 1
        self.basis[7] = 2

        self.colors = [0] * 3 * self.PIXELS_N
        self.dev = apa102.APA102(num_led=self.PIXELS_N)

        self.next = threading.Event()
        self.queue = Queue()
        self.event_loop_task = loop.create_task(self._run())

        self.stop = False

    async def kill(self):
        """Kill event async"""

        self.stop = True

    def wakeup(self):
        if self.development:
            logging.info("Pixels in development mode, WAKEUP")
            return

        def f():
            self._wakeup()

        self.next.set()
        self.queue.put(f)

    def listen(self):
        if self.development:
            logging.info("Pixels in development mode, LISTEN")
            return

        self.next.set()
        self.queue.put(self._listen)

    def think(self):
        if self.development:
            logging.info("Pixels in development mode, THINK")
            return

        self.next.set()
        self.queue.put(self._think)

    def speak(self):
        if self.development:
            logging.info("Pixels in development mode, SPEAK")
            return

        self.next.set()
        self.queue.put(self._speak)

    def off(self):
        if self.development:
            logging.info("Pixels in development mode, OFF")
            return

        self.next.set()
        self.queue.put(self._off)

    async def _run(self):
        while True:
            func = self.queue.get()
            func()

            if self.stop:
                break

            await asyncio.sleep(0.01)

    async def _wakeup(self):
        colors = [0] * 3 * self.PIXELS_N
        for i in range(1, 25):
            colors = [i * v for v in self.basis]
            self.write(colors)
            await asyncio.sleep(0.01)

        self.colors = colors

    async def _listen(self):
        colors = [0] * 3 * self.PIXELS_N
        for i in range(1, 25):
            colors = [i * v for v in self.basis]
            self.write(colors)
            await asyncio.sleep(0.01)

        self.colors = colors

    async def _think(self):
        colors = self.colors

        self.next.clear()
        while not self.next.is_set():
            colors = colors[3:] + colors[:3]
            self.write(colors)
            await asyncio.sleep(0.2)

        t = 0.1
        for i in range(0, 5):
            colors = colors[3:] + colors[:3]
            self.write([(v * (4 - i) / 4) for v in colors])
            await asyncio.sleep(t)
            t /= 2

        self.colors = colors

    async def _speak(self):
        colors = self.colors
        gradient = -1
        position = 24

        self.next.clear()
        while not self.next.is_set():
            position += gradient
            self.write([(v * position / 24) for v in colors])

            if position == 24 or position == 4:
                gradient = -gradient
                await asyncio.sleep(0.2)
            else:
                await asyncio.sleep(0.01)

        while position > 0:
            position -= 1
            self.write([(v * position / 24) for v in colors])
            await asyncio.sleep(0.01)

    async def _off(self):
        self.write([0] * 3 * self.PIXELS_N)

    def write(self, colors):
        if self.development:
            logging.info("Pixels in development mode, WRITE {}".format(colors))
            return
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(
                i, int(colors[3 * i]), int(colors[3 * i + 1]), int(colors[3 * i + 2])
            )

        self.dev.show()


# if __name__ == '__main__':
#     pixels = Pixels()
#
#     while True:
#
#         try:
#             pixels.wakeup()
#             time.sleep(3)
#             pixels.think()
#             time.sleep(3)
#             pixels.speak()
#             time.sleep(3)
#             pixels.off()
#             time.sleep(3)
#         except KeyboardInterrupt:
#             break
#
#     pixels.off()
#     time.sleep(1)
