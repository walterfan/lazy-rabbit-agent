#!/usr/bin/env python
from langserve import RemoteRunnable

remote_chain = RemoteRunnable("http://localhost:8000/chain/")
result = remote_chain.invoke({"language": "chinese", "text": "As you sow, so shall you reap"})
print(result)