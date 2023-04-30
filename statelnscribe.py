from lightning import Plugin
from lndgrpc import lnrpc
import codecs

plugin = Plugin()

@plugin.method("export-channel-state")
def export_channel_state(plugin):
    # Connect to LND node using gRPC
    cert = plugin.rpc.listconfigs()["tls_cert"]
    macaroon = plugin.rpc.invoice("1")["payment_request"]
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'
    creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel('localhost:10009', creds)
    stub = lnrpc.LightningStub(channel)

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
    with open('channelstate.backup', 'wb') as f:
        f.write(response.backup)

    return {'message': 'Channel state exported to channelstate.backup file.'}

plugin.run()