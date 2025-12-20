## utilities for loading sprite data from SFF files.
## leaning heavily on the reference in https://github.com/bitcraft/mugen-tools/blob/master/libmugen/sff.py as SFF's implementation of some things is wonky
from __future__ import annotations

from io import BufferedReader
from struct import unpack
from dataclasses import dataclass

def readbyte(io: BufferedReader) -> int:
    return io.read(1)[0]

def readshort(io: BufferedReader) -> int:
    return unpack('<H', io.read(2))[0]

def readint(io: BufferedReader) -> int:
    return unpack('<I', io.read(4))[0]

@dataclass
class SFFHeader:
    signature: bytes
    verlo3: int
    verlo2: int
    verlo1: int
    verhi: int
    compatverlo3: int
    compatverlo2: int
    compatverlo1: int
    compatverhi: int
    sprite_offset: int
    sprite_total: int
    palette_offset: int
    palette_total: int
    ldata_offset: int
    ldata_total: int
    tdata_offset: int
    tdata_total: int

    @classmethod
    def load(cls, io: BufferedReader) -> SFFHeader:
        sig = io.read(12)
        vers = (readbyte(io), readbyte(io), readbyte(io), readbyte(io))
        _ = io.read(8)
        compat = (readbyte(io), readbyte(io), readbyte(io), readbyte(io))
        _ = io.read(8)
        sprite = (readint(io), readint(io))
        palette = (readint(io), readint(io))
        ldata = (readint(io), readint(io))
        tdata = (readint(io), readint(io))

        return SFFHeader(
            sig,
            vers[0], vers[1], vers[2], vers[3],
            compat[0], compat[1], compat[2], compat[3],
            sprite[0], sprite[1],
            palette[0], palette[1],
            ldata[0], ldata[1],
            tdata[0], tdata[1]
        )
    
@dataclass
class SFFPalette:
    groupno: int
    itemno: int
    numcols: int
    index: int
    data_offset: int
    data_length: int

    buffer: BufferedReader
    _cache: list[tuple[int, int, int]] | None = None

    @classmethod
    def load(cls, io: BufferedReader, header: SFFHeader, member: int) -> SFFPalette:
        # each palette header is 16 bytes long
        offs = 16 * member
        # seek to the offset for this member
        io.seek(header.palette_offset + offs)

        group = readshort(io)
        item = readshort(io)
        cols = readshort(io)
        index = readshort(io)
        data = (readint(io), readint(io))

        return SFFPalette(
            group, item, cols, index, 
            data[0] + header.ldata_offset, data[1], io
        )
    
    @property
    def data(self) -> list[tuple[int, int, int]]:
        if self._cache != None:
            return self._cache

        ## palette data sits in the ldata chunk
        result: list[tuple[int, int, int]] = []
        self.buffer.seek(self.data_offset)

        while self.buffer.tell() < self.data_offset + self.data_length:
            colors = (readbyte(self.buffer), readbyte(self.buffer), readbyte(self.buffer))
            _ = readbyte(self.buffer)
            result.append(colors)

        self._cache = result
        return result

@dataclass
class SFFSprite:
    groupno: int
    itemno: int
    width: int
    height: int
    offsetx: int
    offsety: int
    index: int
    format: int
    depth: int
    data_offset: int
    data_length: int
    palette_index: int
    flags: int

    buffer: BufferedReader
    _cache: bytes | None = None

    @classmethod
    def load(cls, io: BufferedReader, header: SFFHeader, member: int) -> SFFSprite:
        # each sprite header is 28 bytes long
        offs = 28 * member
        # seek to the offset for this member
        io.seek(header.sprite_offset + offs)

        group = readshort(io)
        item = readshort(io)
        width = readshort(io)
        height = readshort(io)
        offset = (readshort(io), readshort(io))
        index = readshort(io)
        format = readbyte(io)
        depth = readbyte(io)
        data = (readint(io), readint(io))
        palette = readshort(io)
        flags = readshort(io)

        # determine whether to load from ldata or tdata
        if flags == 0:
            data = (data[0] + header.ldata_offset, data[1])
        else:
            data = (data[0] + header.tdata_offset, data[1])

        return SFFSprite(
            group, item, width, height,
            offset[0], offset[1], index, format,
            depth, data[0], data[1], palette, flags,
            io
        )
    
    @property
    def data(self) -> bytes:
        if self._cache != None:
            return self._cache

        ## sprite data is already offset to either ldata or tdata depending on flags
        self.buffer.seek(self.data_offset)
        size = readint(self.buffer)
        raw = self.buffer.read(self.data_length - 4)

        ## raw data may need to be decoded (e.g. rle8)
        if self.format == 0:
            self._cache = raw
        elif self.format == 1:
            raise Exception(f"Invalid format used for sprite {self.groupno, self.itemno}")
        elif self.format == 2:
            self._cache = self.rle8(raw, size)
        elif self.format == 3:
            self._cache = self.rle5(raw, size)
        elif self.format == 4:
            self._cache = self.lz5(raw, size)
        else:
            raise Exception(f"Don't currently know how to decode format {self.format} for sprite {self.groupno, self.itemno}")
        
        return self._cache
    
    def palette(self, pal: SFFPalette) -> list[tuple[int, int, int]]:
        ## this function expects the output from `self.data` to be palette-indexed colors.
        colors = pal.data
        indexes = self.data

        ## raw format can only be paletted if the color depth is 8, otherwise color info is encoded into the raw data.
        if self.format == 0 and self.depth != 8:
            raise Exception("Raw-format image cannot have a palette applied unless it uses color depth of 8.")
        
        return [colors[pixel] for pixel in indexes]
        
    def rle8(self, raw: bytes, size: int) -> bytes:
        ## this function produces a block of bytes without paletting applied.
        pass

    def rle5(self, raw: bytes, size: int) -> bytes:
        pass

    def lz5(self, raw: bytes, size: int) -> bytes:
        pass

@dataclass
class SFF:
    header: SFFHeader
    palettes: list[SFFPalette]
    sprites: list[SFFSprite]
    buffer: BufferedReader

    @classmethod
    def load(cls, io: BufferedReader) -> SFF:
        header = SFFHeader.load(io)
        palettes: list[SFFPalette] = []
        sprites: list[SFFSprite] = []

        for index in range(header.palette_total):
            palettes.append(SFFPalette.load(io, header, index))

        for index in range(header.sprite_total):
            sprites.append(SFFSprite.load(io, header, index))

        return SFF(
            header, 
            palettes, 
            sprites,
            io
        )