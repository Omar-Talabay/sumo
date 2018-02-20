# sumo

This app first starts a TCP connection and waits for clients. Each client should provide a valid vehicle ID as integer in an encoded format. After all clients arrive, the user should press enter.
SUMO server will start then. SOUMO will broadcast vehicle information periodically and forwards recieved messages from vehicles in case of danger or whatever....
It stops broadcasting specialized messages in case it receives stop signal from the cleint.

In conclusion, this works as a radio channel and independent radion for each vehicle.
