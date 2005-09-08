#!/usr/bin/env python
# coding: iso-8859-1

# from ConfigParser import SafeConfigParser as ConfigParser
from ConfigParser import ConfigParser as ConfigParser
import os

class Configuration ( object ) :
    _extension = '.ini'
    _default_filename = 'config'
    _default_modulename = 'main'

    def __init__(self, file=None, extension=None):
        self._files = []
        if file :
            self.add_file(file)
        if extension :
            self._extension = extension
        self._modulename = self._default_modulename
        self._dirs = ['.']

        self._value_by_key = {}

    def add_file(self,file):
        self._files.append(file)

    def add_dir(self,dir):
        self._dirs.append(dir)

    def set_modulename(self,modulename):
        self._modulename = modulename

    def get(self,key,default=None):
        if key.lower() in self._value_by_key :
           return self[key.lower()]
        return default

    def __getitem__(self,key):
        return self._value_by_key[key.lower()]

    def __contains__(self,key):
        return key.lower() in self._value_by_key

    def read(self):

        self._files_by_dir = {}
        self._sections_by_file = {}
        self._keys_by_section = {}
        self._value_by_key = {}

        self._dir_by_file = {}
        self._file_by_section = {}
        self._section_by_key = {}
        #self._key_by_value = {}

        self._to_read = {
            'dirs' : self._dirs,
            'files' : self._get_files(),
            'sections' : [self._modulename],
            }

        self._to_add = {
            'dirs' : [],
            'files' : [],
            'sections' : [],
            }

        something_read = True
        while something_read :
            something_read = False

            for key in self._to_add :
                self._to_add[key] = []

            len_before_read = len(self._dir_by_file)
            self._read_dirs(self._to_read['dirs'])
            len_after_read = len(self._dir_by_file)
            if len_before_read != len_after_read :
                something_read = True

            len_to_read = len(self._to_read['files'])
            files_not_read = self._read_files(self._to_read['files'])
            if len_to_read != len(files_not_read) :
                something_read = True

            len_to_read = len(self._to_read['sections'])
            sections_not_read = self._read_sections(self._to_read['sections'])
            if len_to_read != len(sections_not_read) :
                something_read = True

            self._to_read['dirs'] = self._to_add['dirs']
            self._to_read['files'] = files_not_read
            self._to_read['sections'] = sections_not_read

            for file in self._to_add['files'] :
                if file not in self._to_read['files'] :
                    self._to_read['files'].append(file)

            for section in self._to_add['sections'] :
                if section not in self._to_read['sections'] :
                    self._to_read['sections'].append(section)

    def _read_dirs(self, dirs) :
        for dir in dirs :
            for file in os.listdir(dir) :
                fullfile = os.path.join(dir,file)
                if not(os.path.isdir(fullfile)) :
                    if file.lower()[-len(self._extension):] == self._extension :
                        if file not in self._dir_by_file :
                            self._files_by_dir[dir] = self._files_by_dir.get(dir,{})
                            self._files_by_dir[dir][file] = fullfile
                            self._sections_by_file[file] = []
                            self._dir_by_file[file] = dir
                            #print "dir / file : %s / %s" % (dir,file)

    def _read_files(self, files) :
        files_not_read = []

        for file in files :
            fullfile = None
            if file in self._dir_by_file :
                fullfile = self._files_by_dir[self._dir_by_file[file]][file]
            elif os.path.exists(file) :
                fullfile = file
                dir = ''
                self._files_by_dir[dir] = self._files_by_dir.get(dir,{})
                self._files_by_dir[dir][file] = fullfile
                self._sections_by_file[file] = []
                self._dir_by_file[file] = dir
                 
            if fullfile :
                local_parser = ConfigParser()
                local_parser.read(fullfile)

                for section in local_parser.sections() :
                    if section not in self._file_by_section :
                        # self._sections_by_file[file] should exist and be a list
                        self._sections_by_file[file].append(section)
                        self._keys_by_section[section] = []
                        self._file_by_section[section] = file
                        #print "file / section : %s / %s" % (file,section)
            else :
                files_not_read.append(file)
        return files_not_read

    def _read_sections(self, sections) :
        sections_not_read = []

        for section in sections :
            if section in self._file_by_section :
                file = self._file_by_section[section]
                dir = self._dir_by_file[file]
                fullfile = self._files_by_dir[dir][file]
                local_parser = ConfigParser()
                local_parser.read(fullfile)

                for key in local_parser.options(section) :
                    value = local_parser.get(section,key,raw=True)
                    if key in self._to_add :
                        if key == 'dirs' :
                            curdir = os.getcwd()
                            if dir != '' :
                                os.chdir(dir)
                            for subdir in value.split(',') :
                                self._to_add[key].append(os.path.abspath(subdir))
                            os.chdir(curdir)
                        elif key == 'files' :
                            for subfile in value.split(',') :
                                if subfile[-len(self._extension):].lower() == self._extension :
                                    self._to_add[key].append(subfile)
                                else :
                                    self._to_add[key].append(subfile+self._extension)
                        else :
                            self._to_add[key] += value.split(',')
                    elif key not in self._section_by_key :
                        # self._sections_by_file[file] should exist and be a list
                        self._keys_by_section[section].append(key)
                        self._value_by_key[key] = value
                        self._section_by_key[key] = section
                        #self._key_by_value[value] = key
                        #print "section / key / value : %s / %s / %s" % (section,key,value)
            else :
                sections_not_read.append(section)
        return sections_not_read

    def _get_files(self) :
        if len(self._files) > 0 :
            return self._files
        return [self._default_filename+self._extension]

    def __str__(self) :
        result = ""

        result += "[main]\n"
        for key in self._value_by_key :
            section = self._section_by_key[key]
            file = self._file_by_section[section]
            dir = self._dir_by_file[file]
            value = self._value_by_key[key]

            result += "; [%s]  %s\n" % (section,os.path.join(dir,file))
            result += "%s = %s\n" % (key,value)

        return result

class pysvngraphConfiguration ( Configuration ) :
    _extension = '.pysvngraph'

def test() :
    c=Configuration()
    c.read()
    print c

if __name__ == '__main__' :
    test()