# -*- coding: utf-8 -*-
#
# Copyright 2016 Petras Jokubauskas
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any project and source this library is coupled.
# If not, see <http://www.gnu.org/licenses/>.

# The basic reading capabilities of proprietary AidAim Software(tm)
#  SFS (Single File System) (used in bcf technology) is present in
#  this library.

import io
from datetime import datetime, timedelta
import numpy as np
from struct import unpack as strct_unp
import json

import logging
_logger = logging.getLogger(__name__)


class SFSTreeItem(object):
    """Class to manage one internal sfs file.

    Reading, reading in chunks, reading and extracting, reading without
    extracting even if compression is pressent.

    Attributes:
    item_raw_string -- the bytes from sfs file table describing the file
    parent -- the item higher hierarchicaly in the sfs file tree

    Methods:
    read_piece, setup_compression_metadata, get_iter_and_properties,
    get_as_BytesIO_string
    """

    def __init__(self, item_raw_string, parent):
        self.sfs = parent
        self._pointer_to_pointer_table, self.size, create_time, \
        mod_time, some_time, self.permissions, \
        self.parent, _, self.is_dir, _, name, _ = strct_unp(
                       '<iQQQQIi176s?3s256s32s', item_raw_string)
        self.create_time = self._filetime_to_unix(create_time)
        self.mod_time = self._filetime_to_unix(mod_time)
        self.some_time = self._filetime_to_unix(some_time)
        self.name = name.strip(b'\x00').decode('utf-8')
        self.size_in_chunks = self._calc_pointer_table_size()
        if self.is_dir == 0:
            self._fill_pointer_table()

    def _calc_pointer_table_size(self):
        n_chunks = -(-self.size // self.sfs.usable_chunk)
        return n_chunks

    def _filetime_to_unix(self, time):
        """Return recalculated windows filetime to unix time."""
        return datetime(1601, 1, 1) + timedelta(microseconds=time / 10)

    def __repr__(self):
        return '<SFS internal file {0:.2f} MB>'.format(self.size / 1048576)

    def _fill_pointer_table(self):
        """Parse the sfs and populate self.pointers table.

        self.pointer is the sfs pointer table containing addresses of
        every chunk of the file.

        The pointer table if the file is big can extend throught many
        sfs chunks. Differently than files, the pointer table of file have no
        table of pointers to the chunks. Instead if pointer table is larger
        than sfs chunk, the chunk header contains next chunk number (address
        can be calculated using known chunk size and global offset) with
        continuation of file pointer table, thus it have to be read and filled
        consecutive.
        """
        #table size in number of chunks:
        n_of_chunks = -(-self.size_in_chunks //
                       (self.sfs.usable_chunk // 4))
        with open(self.sfs.filename, 'rb') as fn:
            if n_of_chunks > 1:
                next_chunk = self._pointer_to_pointer_table
                temp_string = io.BytesIO()
                for dummy1 in range(n_of_chunks):
                    fn.seek(self.sfs.chunksize * next_chunk + 0x118)
                    next_chunk = strct_unp('<I', fn.read(4))[0]
                    fn.seek(28, 1)
                    temp_string.write(fn.read(self.sfs.usable_chunk))
                temp_string.seek(0)
                temp_table = temp_string.read()
                temp_string.close()
            else:
                fn.seek(self.sfs.chunksize *
                        self._pointer_to_pointer_table + 0x138)
                temp_table = fn.read(self.sfs.usable_chunk)
            self.pointers = np.fromstring(temp_table[:self.size_in_chunks * 4],
                                          dtype='uint32').astype(np.int64) *\
                                                   self.sfs.chunksize + 0x138

    def read_piece(self, offset, length):
        """Read and returns raw byte string of the file without applying
        any decompression.

        Arguments:
        ----------
        offset: seek value
        length: length of the data counting from the offset

        Returns:
        ----------
        io.ByteIO object
        """
        data = io.BytesIO()
        #first block index:
        fb_idx = offset // self.sfs.usable_chunk
        #first block offset:
        fbo = offset % self.sfs.usable_chunk
        #last block index:
        lb_idx = (offset + length) // self.sfs.usable_chunk
        #last block cut off:
        lbco = (offset + length) % self.sfs.usable_chunk
        with open(self.sfs.filename, 'rb') as fn:
            if fb_idx != lb_idx:
                fn.seek(self.pointers[fb_idx] + fbo)
                data.write(fn.read(self.sfs.usable_chunk - fbo))
                for i in self.pointers[fb_idx + 1:lb_idx]:
                    fn.seek(i)
                    data.write(fn.read(self.sfs.usable_chunk))
                if lbco > 0:
                    fn.seek(self.pointers[lb_idx])
                    data.write(fn.read(lbco))
            else:
                fn.seek(self.pointers[fb_idx] + fbo)
                data.write(fn.read(length))
        data.seek(0)
        return data.read()

    def _iter_read_chunks(self, first=0, chunks=False):
        """Generate and return iterator for reading and returning
        sfs internal file in chunks.

        By default it creates iterator for whole file, however
        with kwargs 'first' and 'chunks' the range of chunks
        for iterator can be set.

        Keyword arguments:
        first -- the index of first chunk from which to read. (default 0)
        chunks -- the number of chunks to read. (default False)
        """
        if not chunks:
            last = self.size_in_chunks
        else:
            last = chunks + first
        with open(self.sfs.filename, 'rb') as fn:
            for idx in range(first, last - 1):
                fn.seek(self.pointers[idx])
                yield fn.read(self.sfs.usable_chunk)
            fn.seek(self.pointers[last - 1])
            if last == self.size_in_chunks:
                last_stuff = self.size % self.sfs.usable_chunk
                if last_stuff != 0:
                    yield fn.read(last_stuff)
                else:
                    yield fn.read(self.sfs.usable_chunk)
            else:
                yield fn.read(self.sfs.usable_chunk)

    def setup_compression_metadata(self):
        """ parse and setup the number of compression chunks
        and uncompressed chunk size as class attributes.

        Sets up attributes:
        self.uncompressed_blk_size, self.no_of_compr_blk
        """
        with open(self.sfs.filename, 'rb') as fn:
            fn.seek(self.pointers[0])
            #AACS signature, uncompressed size, undef var, number of blocks
            aacs, uc_size, _, n_of_blocks = strct_unp('<IIII', fn.read(16))
        if aacs == 0x53434141:  # AACS as string
            self.uncompressed_blk_size = uc_size
            self.no_of_compr_blk = n_of_blocks
        else:
            raise ValueError("""The file is marked to be compressed,
but compression signature is missing in the header. Aborting....""")

    def _iter_read_larger_chunks(self, chunk_size=524288):
        """
        Generate and return iterator for reading
        the raw data in sensible sized chunks.
        default chunk size = 524288 bytes (0.5MB)
        """
        chunks = -(-self.size // chunk_size)
        last_chunk = self.size % chunk_size
        offset = 0
        for dummy1 in range(chunks - 1):
            raw_string = self.read_piece(offset, chunk_size)
            offset += chunk_size
            yield raw_string
        if last_chunk != 0:
            raw_string = self.read_piece(offset, last_chunk)
        else:
            raw_string = self.read_piece(offset, chunk_size)
        yield raw_string

    def _iter_read_compr_chunks(self):
        """Generate and return iterator for compressed file with
        zlib or bzip2 compression, where iterator returns uncompressed
        data in chunks as iterator.
        """
        if self.sfs.compression == 'zlib':
            from zlib import decompress as unzip_block
        else:
            from bzip2 import decompress as unzip_block  # lint:ok
        offset = 0x80  # the 1st compression block header
        for dummy1 in range(self.no_of_compr_blk):
            cpr_size, dummy_size, dummy_unkn, dummy_size2 = strct_unp('<IIII',
                                                  self.read_piece(offset, 16))
            # dummy_unkn is probably some kind of checksum but non
            # known (crc16, crc32, adler32) algorithm could match.
            # dummy_size2 == cpr_size + 0x10 which have no use...
            # dummy_size, which is decompressed size, also have no use...
            # as it is the same in file compression_header
            offset += 16
            raw_string = self.read_piece(offset, cpr_size)
            offset += cpr_size
            yield unzip_block(raw_string)

    def get_iter_and_properties(self, larger_chunks=False):
        """Get the the iterator and properties of its chunked size and
        number of chunks for compressed or not compressed data
        accordingly.
        ----------
        Returns:
            (iterator, chunk_size, number_of_chunks)
        """
        if self.sfs.compression == 'None':
            if not larger_chunks:
                return self._iter_read_chunks(), self.sfs.usable_chunk,\
                   self.size_in_chunks
            else:
                return self._iter_read_larger_chunks(chunk_size=larger_chunks),\
                    larger_chunks, -(-self.size // larger_chunks)
        elif self.sfs.compression in ('zlib', 'bzip2'):
            return self._iter_read_compr_chunks(), self.uncompressed_blk_size,\
                   self.no_of_compr_blk
        else:
            raise RuntimeError('file', str(self.sfs.filename),
                               ' is compressed by not known and not',
                               'implemented algorithm.\n Aborting...')

    def get_as_BytesIO_string(self):
        """Get the whole file as io.BytesIO object (in memory!)."""
        data = io.BytesIO()
        data.write(b''.join(self.get_iter_and_properties()[0]))
        return data


class SFS_reader(object):

    """Class to read sfs file.

    SFS is AidAim software's(tm) single file system.
    The class provides basic reading capabilities of such container.
    It is capable to read compressed data in zlib, but
    SFS can contain other compression which is not implemented here.
    It is also not able to read encrypted sfs containers.

    This class can be used stand alone or inherited in construction of
    file readers using sfs technolgy.

    Attributes:
    filename

    Methods:
    get_file
    """

    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'rb') as fn:
            a = fn.read(8)
            if a != b'AAMVHFSS':
                raise TypeError(
                    "file '{0}' is not SFS container".format(filename))
            fn.seek(0x124)  # this looks to be version, as float value is always
            # nicely rounded and at older bcf versions (<1.9) it was 2.40,
            # at new (v2) - 2.60
            version, self.chunksize = strct_unp('<fI', fn.read(8))
            self.sfs_version = '{0:4.2f}'.format(version)
            self.usable_chunk = self.chunksize - 32
            fn.seek(0x140)
            #the sfs tree and number of the items / files + directories in it,
            #and the number in chunks of whole sfs:
            self.tree_address, self.n_tree_items, self.sfs_n_of_chunks =\
                                                 strct_unp('<III', fn.read(12))
        self._setup_vfs()

    def _setup_vfs(self):
        with open(self.filename, 'rb') as fn:
            #check if file tree do not exceed one chunk:
            n_file_tree_chunks = -((-self.n_tree_items * 0x200) //
                                             (self.chunksize - 512))
            if n_file_tree_chunks is 1:
                fn.seek(self.chunksize * self.tree_address + 0x138)
                raw_tree = fn.read(0x200 * self.n_tree_items)
            else:
                temp_str = io.BytesIO()
                for i in range(n_file_tree_chunks):
                    # jump to tree/list address:
                    fn.seek(self.chunksize * self.tree_address + 0x118)
                    # next tree/list address:
                    self.tree_address = strct_unp('<I', fn.read(4))[0]
                    fn.seek(28, 1)
                    temp_str.write(fn.read(self.chunksize - 512))
                temp_str.seek(0)
                raw_tree = temp_str.read(self.n_tree_items * 0x200)
                temp_str.close()
            # temp flat list of items:
            temp_item_list = [SFSTreeItem(raw_tree[i * 0x200:(i + 1) * 0x200],
                                       self) for i in range(self.n_tree_items)]
            # temp list with parents of items
            paths = [[h.parent] for h in temp_item_list]
        #checking the compression header which can be different per file:
        self._check_the_compresion(temp_item_list)
        if self.compression in ('zlib', 'bzip2'):
            for c in temp_item_list:
                if not c.is_dir:
                    c.setup_compression_metadata()
        # Shufling items from flat list into dictionary tree:
        while not all(g[-1] == -1 for g in paths):
            for f in range(len(paths)):
                if paths[f][-1] != -1:
                    paths[f].extend(paths[paths[f][-1]])
        names = [j.name for j in temp_item_list]
        names.append('root')  # temp root item in dictionary
        for p in paths:
            for r in range(len(p)):
                p[r] = names[p[r]]
        for p in paths:
            p.reverse()
        root = {}
        for i in range(len(temp_item_list)):
            dir_pointer = root
            for j in paths[i]:
                if j in dir_pointer:
                    dir_pointer = dir_pointer[j]
                else:
                    dir_pointer[j] = {}
                    dir_pointer = dir_pointer[j]
            if temp_item_list[i].is_dir:
                dir_pointer[temp_item_list[i].name] = {}
            else:
                dir_pointer[temp_item_list[i].name] = temp_item_list[i]
        # and finaly Virtual file system:
        self.vfs = root['root']

    def _check_the_compresion(self, temp_item_list):
        """parse, check and setup the self.compression"""

        with open(self.filename, 'rb') as fn:
            #Find if there is compression:
            for c in temp_item_list:
                if not c.is_dir:
                    fn.seek(c.pointers[0])
                    if fn.read(4) == b'\x41\x41\x43\x53':  # string AACS
                        fn.seek(0x8C, 1)
                        compression_head = fn.read(2)
                        byte_one = strct_unp('BB', compression_head)[0]
                        if byte_one == 0x78:
                            self.compression = 'zlib'
                        elif compression_head == b'\x42\x5A':
                            self.compression = 'bzip2'
                        else:
                            self.compression = 'unknown'
                    else:
                        self.compression = 'None'
                    # compression is global, can't be diferent per file in sfs
                    break

    def print_file_tree(self):
        """print the internal file/dir tree of sfs container
        as json string
        """
        tree = json.dumps(self.vfs, sort_keys=True, indent=4, default=str)
        print(tree)

    def get_file(self, path):
        """Return the SFSTreeItem (aka internal file) object from
        sfs container.

        Arguments:
        path -- internal file path in sfs file tree. Path accepts only
            standard - forward slash for directories.

        Returns:
        object (SFSTreeItem), which can be read into byte stream, in
        chunks or whole using objects methods.

        Example:
        to get "file" object 'kitten.png' in folder 'catz' which
        resides in root directory of sfs, you would use:

        >>> instance_of_SFSReader.get_file('catz/kitten.png')

        See also:
        SFSTreeItem
        """
        item = self.vfs
        try:
            for i in path.split('/'):
                item = item[i]
            return item
        except KeyError:
            print("""Check the requested path!
There is no such file or folder in this single file system.
Try printing out the file tree with print_file_tree method""")