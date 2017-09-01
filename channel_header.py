class ChannelHeader:
  def __init__(self,seq,name):
    self.seq = seq
    self.name = name
    self.offset_in_chunk = -1
    self.sample_rate = -1
    #chunk_size means number of elements in one chunk
    self.chunk_size = -1
    