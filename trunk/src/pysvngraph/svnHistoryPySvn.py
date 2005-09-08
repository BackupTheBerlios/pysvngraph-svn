#!/usr/bin/env python
# coding: iso-8859-1

import cPickle as Serializer
import copy_reg
import pysvn
from svnHistory import svnHistoryBase

# -------------------------------------------------------------------
# pysvn + pickle
# -------------------------------------------------------------------

_type_revision = type(pysvn.Revision(pysvn.opt_revision_kind.head))

def _revision_construct(kindstr,arg) :
    arg = Serializer.loads(arg)
    assert ((kindstr != 'date') and (kindstr != 'number')) or arg != None
    kind = getattr(pysvn.opt_revision_kind,kindstr)
    if (kindstr == 'date') or (kindstr == 'number') :
        revision = pysvn.Revision(kind,arg)
    else :
        revision = pysvn.Revision(kind)

    return revision

def _revision_reduce(revision) :
    assert type(revision) == _type_revision
    # print "  (%s)" % (revision,)
    return _revision_construct, (str(revision.kind),Serializer.dumps(revision.date or revision.number))

def _register_revision() :
    copy_reg.pickle(_type_revision,_revision_reduce,_revision_construct)

_register_revision()

# -------------------------------------------------------------------
# functions
# -------------------------------------------------------------------

def get_loghistory(url) :
    svnclient = pysvn.Client()
    loghistory = svnclient.log(url,discover_changed_paths=True,strict_node_history=True)
    return loghistory

def save_loghistory_(loghistory,filename) :
    handle = file(filename,"wb")
    Serializer.dump(loghistory,handle)
    handle.close()

def get_loghistory_(url) :
    import os
    import md5
    filename = "loghistory-"+md5.new(url).hexdigest()
    if os.path.exists(filename) :
        handle = file(filename,"rb")
        loghistory = Serializer.load(handle)
        handle.close()
    else :
        loghistory = get_loghistory(url)
        save_loghistory_(loghistory,filename)
        pass
    return loghistory

# ---------------------------------------- class : svnHistoryPySvn --
# -------------------------------------------------------------------

class svnHistoryPySvn (svnHistoryBase) :
    def __init__(self,url,*args,**kwargs) :
        self._url = url
        self._pysvnhistory = get_loghistory(url)
        self._pysvnhistory.reverse()

    def __iter__(self) :
        """Iterator for svnHistory. This method will return a svnHistoryPySvnIterator who will give svnRevision informations"""
        class svnHistoryPySvnIterator :
            def __init__(self,pysvnhistory) :
                self._pysvnhistory = pysvnhistory
                self._sub_iterator = iter(self._pysvnhistory)
            def next(self) :
                pysvnhistory_line = self._sub_iterator.next()
                changelist = []
                for changed_path in pysvnhistory_line['changed_paths'] :
                    changelist.append(svnFileChange(changed_path['action'],changed_path['path'],changed_path['copyfrom_path'],changed_path['copyfrom_revision']))
                return svnRevision(number=pysvnhistory_line['revision'].number,changelist=changelist)