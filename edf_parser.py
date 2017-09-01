#coding=utf-8 
import io
import struct
from channel_header import ChannelHeader

# Input
#   edf_filename: full path name of EDF file
# Return
#   data_map: key=channel_name, value=data list
#   cHdrList: header info of each channel
def readRawDataFromEdf(edf_filename):
  with io.open(edf_filename, 'rb') as f:
    cHdrList = readHeader(f)
    #DEBUG
    chunk_size = 0
    for cHdr in cHdrList:
      print "%s, sample_rate=%d" % (cHdr.name, cHdr.sample_rate)
      chunk_size = chunk_size + cHdr.sample_rate
    print "total bytes in one chunk: %d" % ((2*chunk_size))
    data_map = readData(f, cHdrList)
  
  return data_map,cHdrList

#read header information from EDF file stream
#INPUT f: handle to EDF file, caller must gurantee the position is set to START of the file
#RETURN cHdrList: a list, each element represent a channel
def readHeader(f):
  #2: Process first 256 bytes to get number of channels, and time length for each chunk
  f.seek(243,io.SEEK_CUR)
  chunk_time_len = int(f.read(8))
  #print chunk_time_len
  num_of_channels = int(f.read(4))
  #print num_of_channels
    
  #read num_of_channels*16 byte for names
  cHdrList = []
  for cid in range(num_of_channels):
    channel_name = str(f.read(16)).strip()
    cHdrList.append(ChannelHeader(cid, channel_name))
    
  #Skip data until sample rate
  f.seek(num_of_channels*200, io.SEEK_CUR)
    
  #read sample rate of each channel
  offset = 0
  for cid in range(num_of_channels):
    chunk_size = int(f.read(8))
    cHdrList[cid].offset_in_chunk = offset
    cHdrList[cid].chunk_size = chunk_size
    cHdrList[cid].sample_rate = chunk_size / chunk_time_len
    
  #skip reserved field
  f.seek(num_of_channels*32 + 1, io.SEEK_CUR)
  
  return cHdrList

#read data from EDF file, each data is a 16 bits integer with sign
#INPUT f: handle to EDF file, caller must gurantee the position is set to START + (num_of_channel + 1 )*256, i.e. the start position of data section
#RETURN data_map: key=channel_name, value=data list
def readData(f, cHdrList):
  #prepare the result data
  data_map = {}
  for cHdr in cHdrList:
    data_map[cHdr.name]=[]
  
  #read each channel 
  eof = False
  chunk_cnt = 0
  while True:
    for cHdr in cHdrList:
      #read data for only one channel in one chunk
      for dataIdx in range(cHdr.chunk_size):
        data_array = f.read(2)
        #DEBUG
        #print data_array.encode('hex')
        if (len(data_array) == 0):
          eof = True
          break
        #unpack using little-endian
        data = struct.unpack('<h', data_array)[0]
        data_map[cHdr.name].append(data)
      
      if eof:
        break
    
    chunk_cnt = chunk_cnt +1
    if eof:    
      print "Chunk_count = %d" % (chunk_cnt)
      break
  
  return data_map  

def writeDataIntoDisk(filename, dataList):
  with open(filename,'w') as f:
    for data in dataList:
      f.write("%d," % data)
      
if __name__	== '__main__':
  filename =unicode("0824_170620_Lava2.0初次实测.edf","utf8")
  data_map,cHdrList = readRawDataFromEdf(filename)
  
  for cHdr in cHdrList:
    writeDataIntoDisk("_".join([filename, cHdr.name, str(cHdr.sample_rate)]), data_map[cHdr.name])