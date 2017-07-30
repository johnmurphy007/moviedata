import paho.mqtt.client as mqtt
# Maybe consider using threading (object) instead of thread (function)
from thread import *  # allowing multiple connections
import scanForFilms


host_mqtt_broker = "192.168.1.71"
port_mqtt = 1883

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hello/world")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "hello/world":
        print "Topic Match found"
        if msg.payload == "scanForFilms":
            print "Payload Match found"
        # Start new thread: takes 1st argument as a function name to be run, second is the tuple of arguments to the function
            start_new_thread(clientthread, (99,))

def clientthread(a):
    scanForFilms.main()
    # PERFORM A TEST ON scanForFilms (it should return something)
    # Publish a mqtt if success or failure.
    return

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# SSL/TLS support:
    #client.tls_set("mosquitto.org.crt") # http://test.mosquitto.org/ssl/mosquitto.org.crt
    #client.connect("127.0.0.1", 8883)
    #client.subscribe("bbc/#")

#client.connect("iot.eclipse.org", 1883, 60)
client.connect(host_mqtt_broker, port_mqtt, 60)
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
