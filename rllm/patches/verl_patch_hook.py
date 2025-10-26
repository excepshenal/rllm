import wrapt

_TARGET = "verl.workers.rollout.vllm_rollout.vllm_rollout_spmd"


def setup():
    @wrapt.when_imported(_TARGET)
    def _patch(mod):
        # Your replacement method, defined here so nothing heavy is imported early.
        def _patched_init_zeromq(self) -> str:
            # --- All imports are inside the patch ---
            import getpass
            import os
            import asyncio  # <-- Import asyncio
            
            import zmq.asyncio  # <-- Use asyncio-compatible ZMQ
            import ray
            from ray.util.utils import is_valid_ipv6_address
            # ----------------------------------------

            tensor_parallel_size = self.config.tensor_model_parallel_size
            local_world_size = int(os.environ["RAY_LOCAL_WORLD_SIZE"])
            socket_type = "ipc" if tensor_parallel_size <= local_world_size else "tcp"

            # Use the asyncio-compatible ZMQ context
            context = zmq.asyncio.Context()
            self.socket = context.socket(zmq.REP)

            if socket_type == "ipc":
                # This is already unique, no lock needed.
                pid = os.getpid()
                user = getpass.getuser()
                address = f"ipc:///tmp/verl_vllm_zmq_{pid}_{user}.ipc"
                self.socket.bind(address)
            else:
                # This is the correct, race-condition-free way to get a port.
                # 1. Get the node IP
                ip = ray.util.get_node_ip_address().strip("[]")
                
                # 2. Bind to port 0 (tells the OS to pick any free port)
                if is_valid_ipv6_address(ip):
                    self.socket.setsockopt(zmq.IPV6, 1)
                    self.socket.bind(f"tcp://[{ip}]:0")
                else:
                    self.socket.bind(f"tcp://{ip}:0")
                
                # 3. Ask ZMQ which address it actually bound to
                address = self.socket.getsockopt_string(zmq.LAST_ENDPOINT)

            # Use asyncio loop as requested
            loop = asyncio.get_running_loop()
            self.zmq_loop_task = loop.create_task(self._loop_forever())

            return address

        # Apply the patch to the class
        Cls = getattr(mod, "vLLMAsyncRollout", None)
        if Cls is not None:
            Cls._init_zeromq = _patched_init_zeromq