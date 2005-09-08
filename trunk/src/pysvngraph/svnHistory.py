#!/usr/bin/env python
# coding: iso-8859-1

# ------------------------------------------ class : svnFileChange --
# -------------------------------------------------------------------

class svnFileChange :
    CHANGE_TYPE_ADDED    = 'A'
    CHANGE_TYPE_MODIFIED = 'M'
    CHANGE_TYPE_DELETED  = 'D'
    CHANGE_TYPE_REPLACED = 'R'

    def __init__( self, change_type, filename, fromfile=None, fromrev=None ) :
        self._change_type = change_type
        self._filename    = filename
        self._fromfile    = fromfile
        self._fromrev     = fromrev

    def change_type (self) : return self._change_type
    def filename    (self) : return self._filename
    def fromfile    (self) : return self._fromfile
    def fromrev     (self) : return self._fromrev

    def is_svn_file_change (self) : return True
    def __repr__ (self) : return "svnFileChange(%r,%r,%r,%r)" % (self._change_type,self._filename,self._fromfile,self._fromrev)

# -------------------------------------------- class : svnRevision --
# -------------------------------------------------------------------

class svnRevision :
    def __init__( self, number, comment=None, changelist=[], author=None, date=None ) :
        self._number = number
        self._comment = comment
        self._changelist = changelist
        self._author = author
        self._date = date

    def number( self ) : return self._number
    def comment( self ) : return self._comment
    def author( self ) : return self._author
    def date( self ) : return self._date
    def __iter__(self) :
        """Iterator for svnRevision. This method will return a svnRevisionIterator who will give a svnFileChange"""
        class svnRevisionIterator :
            def __init__(self,changelist) :
                self._sub_iterator = iter(changelist)
            def next(self) :
                element = self._sub_iterator.next()
                if hasattr(element,'is_svn_file_change') :
                    return element
                fromfile = None
                fromrev = None
                if len(element) > 2 :
                    fromfile = element[2]
                if len(element) > 3 :
                    fromrev = element[3]
                return svnFileChange( element[0], element[1], fromfile, fromrev )
        #print "--(%r)--" % (self._changelist,)
        return svnRevisionIterator(self._changelist)

# ----------------------------------------- class : svnHistoryBase --
# -------------------------------------------------------------------

class svnHistoryBase :
    CHANGE_TYPE_ADDED    = svnFileChange.CHANGE_TYPE_ADDED
    CHANGE_TYPE_MODIFIED = svnFileChange.CHANGE_TYPE_MODIFIED
    CHANGE_TYPE_DELETED  = svnFileChange.CHANGE_TYPE_DELETED
    CHANGE_TYPE_REPLACED = svnFileChange.CHANGE_TYPE_REPLACED

    def __init__(self,url,*args,**kwargs) :
        pass
    def __iter__(self) :
        """Iterator for svnHistory. This method will return a svnHistoryIterator who will give svnRevision informations"""
        pass

# ----------------------------------------- class : svnHistoryFile --
# -------------------------------------------------------------------

class svnHistoryFile (svnHistoryBase) :
    CHANGED_PATH_LANG = {
        'Changed paths:' : 'en',
        'Chemins modifi‚s :' : 'fr',
        }
    FROM_LANG = {
        'en' : ' (from ',
        'fr' : ' (de ',
        }
    def __init__(self,url,filename) :
        self._url = url
        self._filename = filename

        self._revisions = {}

        handle = file(filename,'rt')

        wait_for_new_item = True
        wait_for_revision_line = False
        wait_for_changed_paths_line = False
        wait_for_changed_paths = False
        wait_for_comment = False

        lines_of_comment = 0

        lines_to_ignore = 0
        #lines_to_ignore_for_futur = 0

        lang = 'en'

        revision = None
        author = None
        date = None
        changed_files = []
        comment = ""

        for line in handle :
            if line[-1] in ('\r','\n')  :
                crindex = -2
                while line[crindex:crindex+1] in ('\r','\n') :
                    crindex-=1
                line = line[:crindex+1]

            if lines_to_ignore>0 :
                lines_to_ignore -= 1
            elif wait_for_new_item :
                if line[:72]=='-'*72 :
                    wait_for_new_item = False
                    wait_for_revision_line = True
                else :
                    pass
                    #print line

                # else wait for new item on next line
            elif wait_for_revision_line :
                revision_infos = line.split(' | ')
                if len(revision_infos) != 4 :
                    # ERROR
                    pass
                else :
                    try :
                        revision = int(revision_infos[0][1:])
                    except :
                        # ERROR
                        pass
                    author = revision_infos[1]
                    datestr = revision_infos[2]
                    try :
                        date = time.mktime(map(lambda x,y:int(datestr[x:y]),(0,5,8,11,14,17),(4,7,10,13,16,19))+[0,0,0])
                    except :
                        # ERROR
                        pass
                    try :
                        # lines_to_ignore_for_futur = int(revision_infos[3][:revision_infos[3].find(' ')])
                        lines_of_comment = int(revision_infos[3][:revision_infos[3].find(' ')])
                    except :
                        # ERROR
                        pass

                wait_for_revision_line = False
                wait_for_changed_paths_line = True
            elif wait_for_changed_paths_line :
                if line in self.CHANGED_PATH_LANG :
                    wait_for_changed_paths_line = False
                    wait_for_changed_paths = True
                    lang = self.CHANGED_PATH_LANG[line]
                else :
                    wait_for_changed_paths_line = False
                    wait_for_comment = True
            elif wait_for_changed_paths :
                if len(line) >= 3 :
                    # This is ugly, nothing forbid a file name to contains ' (from '
                    # In fact, you can't really parse thoses line.
                    # We'll take as true, the false assertion that the last ' (from ' is the limit between
                    # the destination and the source.
                    frompos = line.rfind(self.FROM_LANG[lang])
                    revseppos = line.rfind(':')

                    change_type = line[3:4]
                    if frompos > 0 :
                        changed_filename = line[5:frompos]
                        fromfile = line[frompos+len(self.FROM_LANG[lang]):revseppos]
                        fromrev = int(line[revseppos+1:-1])
                        changed_files.append(svnFileChange(change_type,changed_filename,fromfile,fromrev))
                    else :
                        changed_filename = line[5:]
                        changed_files.append(svnFileChange(change_type,changed_filename))
                else :
                    wait_for_changed_paths = False
                    wait_for_comment = True

            elif wait_for_comment :
                comment += line+"\n"
                lines_of_comment-=1

                if lines_of_comment == 0 :
                    # Adding a new revision
                    self._revisions[revision] = svnRevision(number=revision,changelist=changed_files,comment=comment,author=author,date=date)

                    revision = None
                    author = None
                    date = None
                    changed_files = []
                    comment = ""

                    wait_for_comment = False
                    wait_for_new_item = True


        handle.close()

    def __iter__(self) :
        """Iterator for svnHistory. This method will return a svnHistoryFileIterator who will give svnRevision informations"""
        class svnHistoryFileIterator :
            def __init__( self, revisions ) :
                self._revisions = revisions
                self._revision_list = self._revisions.keys()
                self._revision_list.sort()
                self._sub_iterator = iter(self._revision_list)
            def next(self) :
                next_revision = self._sub_iterator.next()
                return self._revisions[next_revision]
        return svnHistoryFileIterator(self._revisions)

if __name__ == '__main__' :
    from main import main
    main()