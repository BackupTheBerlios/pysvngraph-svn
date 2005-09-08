#!/usr/bin/env python
# coding: iso-8859-1

class svnAction :
    """This class represent an action that can be done on a SVN repository"""

    ACTIONTYPE_CREATION = 0
    ACTIONTYPE_TAG      = 1
    ACTIONTYPE_WORK     = 2
    ACTIONTYPE_DELETE   = 3
    ACTIONTYPE_MERGE    = 4
    ACTIONTYPE_IGNORE   = 5

    def __init__(self,actionType,branch,revision,branchFrom=None,revisionFrom=None,branchFromSource=None,revisionFromSource=None) :
        self._actionType = actionType
        self._branch = branch
        self._revision = revision
        self._branchFrom = branchFrom
        self._revisionFrom = revisionFrom
        self._branchFromNoTags = None
        self._revisionFromNoTags = None
        self._deleted = False

        # FromSource for merge
        # A merge occurs from < FromSource > to < From > and end into < >
        self._branchFromSource = branchFromSource
        self._revisionFromSource = revisionFromSource
        self._branchFromSourceNoTags = None
        self._revisionFromSourceNoTags = None


    def actionType(self) : return self._actionType
    def branch(self) : return self._branch
    def revision(self) : return self._revision
    def branchFrom(self) : return self._branchFrom
    def revisionFrom(self) : return self._revisionFrom
    def branchFromNoTags(self) : return self._branchFromNoTags or self._branchFrom
    def revisionFromNoTags(self) : return self._revisionFromNoTags or self._revisionFrom
    def deleted(self) : return self._deleted

    def branchFromSource(self) : return self._branchFromSource
    def revisionFromSource(self) : return self._revisionFromSource
    def branchFromSourceNoTags(self) : return self._branchFromSourceNoTags or self._branchFromSource
    def revisionFromSourceNoTags(self) : return self._revisionFromSourceNoTags or self._revisionFromSource

    def setActionType(self,actionType) : self._actionType = actionType
    def setRevisionFrom(self,revisionFrom) : self._revisionFrom = revisionFrom

    def setBranchFromNoTags(self,branchFromNoTags) : self._branchFromNoTags = branchFromNoTags
    def setRevisionFromNoTags(self,revisionFromNoTags) : self._revisionFromNoTags = revisionFromNoTags
    def setBranchFromSourceNoTags(self,branchFromSourceNoTags) : self._branchFromSourceNoTags = branchFromSourceNoTags
    def setRevisionFromSourceNoTags(self,revisionFromSourceNoTags) : self._revisionFromSourceNoTags = revisionFromSourceNoTags

    def setDeleted(self,deleted=True) : self._deleted = deleted

    def __str__(self) : return (self._branchFrom == None) and "<%s:[%s:%d]>" % ("CTWDMI"[self._actionType],self._branch,self._revision) or "<%s:[%s:%d]<--[%s:%d]>" % ("CTWDMI"[self._actionType],self._branch,self._revision,self._branchFrom,self._revisionFrom)
    def __cmp__(self,elem) :
        return cmp( self._revision     , elem._revision     ) or \
               cmp( self._branch       , elem._branch       ) or \
               cmp( self._actionType   , elem._actionType   ) or \
               cmp( self._revisionFrom , elem._revisionFrom ) or \
               cmp( self._branchFrom   , elem._branchFrom   ) or \
               0



