init -999 python:
    try:
        from pypresence import Presence
        import time
        pypresence_available = True
    except ImportError:
        pypypresence_available = False

    RPC = None
    rpc_start_time = None

    def js_start_rpc():
        """
        Connects to Discord RPC. Should be called only once.
        """
        global RPC, rpc_start_time
        if not pypresence_available or RPC is not None:
            return

        try:
            client_id = '1436898855886131212'
            RPC = Presence(client_id)
            RPC.connect()
            rpc_start_time = int(time.time())
        except Exception as e:
            print(f"Failed to connect to Discord RPC: {e}")
            RPC = None
            rpc_start_time = None

    def js_stop_rpc():
        """
        Closes the connection to Discord RPC.
        """
        global RPC, rpc_start_time
        if RPC:
            try:
                RPC.close()
            except Exception as e:
                print(f"Failed to close Discord RPC: {e}")
            finally:
                RPC = None
                rpc_start_time = None

    def js_update_rpc(details=None, state=None, large_image='faelogo', large_text=None, small_image=None, small_text=None):
        """
        Updates the Discord Rich Presence status.
        """
        if RPC:
            try:
                RPC.update(
                    details=details if details is not None else ___("Spending Time With Sayori"),
                    state=state,
                    large_image=large_image,
                    large_text=large_text if large_text is not None else ___("Just Sayori"),
                    small_image=small_image,
                    small_text=small_text,
                    start=rpc_start_time
                )
            except Exception as e:
                print(f"Failed to update Discord RPC: {e}")
