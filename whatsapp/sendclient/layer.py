import logging
import threading

from yowsup.common.tools import Jid
from yowsup.layers import YowLayerEvent, EventCallback
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

logger = logging.getLogger(__name__)

EVENT_SEND_MESSAGE = "plcmon.sendMessage"


class SendLayer(YowInterfaceLayer):
    def __init__(self):
        super(SendLayer, self).__init__()
        self.lock = threading.Condition()

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        print("Got message %s from %s" % (messageProtocolEntity, messageProtocolEntity.getFrom(False)))

        self.toLower(messageProtocolEntity.ack())

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    @EventCallback(EVENT_SEND_MESSAGE)
    def onSendMessage(self, event):
        with self.lock:
            phone, message = [event.getArg("destination"), event.getArg("message")]

            messageEntity = TextMessageProtocolEntity(message, to=Jid.normalize(phone))
            self.toLower(messageEntity)
