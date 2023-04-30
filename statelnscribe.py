import grpc
import os
import codecs
from lndgrpc import lnrpc

# Connect to LND node using gRPC
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

# open tls file
# TODO: configure path
cert = open('tls.cert', 'rb').read()
creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', creds)
stub = lnrpc.LightningStub(channel)

try:
    # Call listchannels gRPC method
    response = stub.ListChannels(lnrpc.ListChannelsRequest())

    # Print channel state and balance
    for channel in response.channels:
        print("Channel ID:", codecs.encode(channel.chan_id, 'hex'))
        print("Channel state:", channel.channel_status)
        print("Local balance:", channel.local_balance)
        print("Remote balance:", channel.remote_balance)

    # Call exportchanbackup gRPC method
    response = stub.ExportChannelBackup(lnrpc.ChanBackupExportRequest())

    # Save channel backup to file
    #TODO: update file name with channel ID & date
    with open('channelstate.backup', 'wb') as f:
        f.write(response.backup)

except grpc.RpcError as e:
    print("Error occurred during gRPC call: ", e)

finally:
    # close gRPC channel
    channel.close()
