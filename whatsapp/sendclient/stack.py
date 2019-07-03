from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.stacks import YowStackBuilder

from .layer import SendLayer, EVENT_SEND_MESSAGE


class YowsupSendStack(object):
    def __init__(self, profile):
        stackBuilder = YowStackBuilder()

        self._stack = (stackBuilder
                       .pushDefaultLayers()
                       .push(SendLayer)
                       .build())

        self._stack.setProfile(profile)

    def set_prop(self, key, val):
        self._stack.setProp(key, val)

    def send_message(self, message):
        # TODO: is broadcastEvent thread safe?
        self._stack.broadcastEvent(YowLayerEvent(
            EVENT_SEND_MESSAGE, message=message))

    def start(self):
        self._stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        self._stack.loop()
