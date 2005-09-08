#!/usr/bin/env python
# coding: iso-8859-1

class _myset :
    '''Local set definition for python < 2.4'''
    def __init__(self,elementset=None):
        self._set = []
        if elementset :
            for element in elementset :
                self.add(element)
    def add(self,element):
        if element not in self._set :
            self._set.append(element)
    def remove(self,element):
        try:
            self._set.remove(element)
        except ValueError :
            raise KeyError(element)
    def __contains__(self,element) :
        return element in self._set
    def __len__(self) :
        return len(self._set)
    def __iter__(self):
        return iter(self._set)
        # for item in self._set :
        #     yield item
    def __dict__(self):
        return dict(self._set)

myset = _myset

class svnRepository :
    """This class represent the set of svnActions that can be done in a SVN repository"""
    def __init__(self,url,mainbranch) :
        """Create a svnRepository"""
        self._url = url
        self._mainbranch = mainbranch

        self._actions = []
        self._revisions_to_ignore = myset()

        self._author_by_revision = {}
        self._date_by_revision = {}

        self._usefull_revisions_by_author = {}

        self._actions_by_branch = None
        self._revisions_by_branch = None

        self._revisionssorted_by_branch = None
        self._actions_by_revision = None
        self._actions_by_revision_branch = None
        self._tags_by_revision_branch = None
        self._actions_by_actionType = None

        self._branches = None
        self._revisions = None
        self._revisions_nowork = None

        self._resolved = False

    def add_info_revision(self, revision, author=None, date=None):
        if revision != None :
            if author != None :
                self._author_by_revision[revision] = author
            if date != None :
                self._date_by_revision[revision] = date

    def add_action(self, action):
        """Add a new action within the repository"""

        self._resolved = False

        # ---- actions ----

        self._actions.append(action)

        if action.actionType() == action.ACTIONTYPE_IGNORE :
            self._revisions_to_ignore.add(action.revision())
            print "REVISION IGNORE : %d" % (action.revision(),)
        if action.actionType() == action.ACTIONTYPE_MERGE :
            print "REVISION MERGE : %d  (%s)" % (action.revision(),action.branch())

    def resolv(self) :
        """Create the internal structure of the repository"""

        if self._resolved :
            return None

        self._actions_by_branch = {}
        self._revisions_by_branch = {}

        self._actions.sort()
        for action in self._actions :
            actionType = action.actionType()
            branch = action.branch()
            revision = action.revision()
            branchFrom = action.branchFrom()
            revisionFrom = action.revisionFrom()

            if revision not in self._revisions_to_ignore :
                # ---- actions_by_branch ----

                self._actions_by_branch[branch] = self._actions_by_branch.get(branch,[])
                self._actions_by_branch[branch].append(action)

                if branchFrom != None and branchFrom != branch :
                    self._actions_by_branch[branchFrom] = self._actions_by_branch.get(branchFrom,[])
                    self._actions_by_branch[branchFrom].append(action)

                # ---- revisions_by_branch ----

                self._revisions_by_branch[branch] = self._revisions_by_branch.get(branch,myset())
                self._revisions_by_branch[branch].add(revision)
                # revisionFrom is meanning-less for _revisions_by_branch


        self._revisionssorted_by_branch = {}
        self._actions_by_revision = {}
        self._actions_by_revision_branch = {}
        self._tags_by_revision_branch = {}
        self._actions_by_actionType = {}

        for branch in self._revisions_by_branch :

            # ---- revisionssorted_by_branch ----

            self._revisionssorted_by_branch[branch] = list(self._revisions_by_branch[branch])
            self._revisionssorted_by_branch[branch].sort()

        for branch in self._actions_by_branch :
            has_worked = False

            action_of_creation = None

            for action in self._actions_by_branch[branch] :

                #----------------------------------------------------
                # 1) We're checking if we've worked in the branch
                #----------------------------------------------------

                if action.actionType() in (action.ACTIONTYPE_WORK, action.ACTIONTYPE_MERGE) :
                    # if the branch associate with action is the current branch
                    if action.branch() == branch :
                        has_worked = True

                #----------------------------------------------------
                # 2) We're putting true "From" revision
                #----------------------------------------------------

                if action.branchFrom() == branch and action.revisionFrom() != None :
                    branchFrom = action.branchFrom()
                    revisionFrom = action.revisionFrom()
                    revisions = self._revisionssorted_by_branch[branchFrom]
                    if len(revisions)>0 :
                        real_revisionFrom = revisions[0]
                        for revision in revisions :
                            if revision <= revisionFrom :
                                real_revisionFrom = revision
                        action.setRevisionFrom(real_revisionFrom)

                        #--------------------------------------------
                        # 3) We're setting up _actions_by_revision and
                        #    _actions_by_revision_branch
                        #--------------------------------------------

                        # ---- actions_by_revision ----

                        self._actions_by_revision[action.revisionFrom()] = self._actions_by_revision.get(action.revisionFrom(),[])
                        self._actions_by_revision[action.revisionFrom()].append(action)

                        # ---- actions_by_revision_branch ----

                        revision_branch = (action.revisionFrom(),action.branchFrom())
                        #print "  AF %s:%s %s" % (revision_branch[0],revision_branch[1],action)
                        self._actions_by_revision_branch[revision_branch] = self._actions_by_revision_branch.get(revision_branch,[])
                        self._actions_by_revision_branch[revision_branch].append(action)

                #----------------------------------------------------
                # 4) We're setting up _actions_by_revision and
                #    _actions_by_revision_branch
                #----------------------------------------------------

                if action.branch() == branch :
                    # ---- actions_by_revision ----

                    self._actions_by_revision[action.revision()] = self._actions_by_revision.get(action.revision(),[])
                    self._actions_by_revision[action.revision()].append(action)

                    # ---- actions_by_revision_branch ----

                    revision_branch = (action.revision(),action.branch())
                    #print "  A  %s:%s %s" % (revision_branch[0],revision_branch[1],action)
                    self._actions_by_revision_branch[revision_branch] = self._actions_by_revision_branch.get(revision_branch,[])
                    self._actions_by_revision_branch[revision_branch].append(action)

                #----------------------------------------------------
                # A) Update "deleted" from actions
                #----------------------------------------------------

                if action.branch() == branch :
                    if action.actionType() in (action.ACTIONTYPE_CREATION, action.ACTIONTYPE_TAG) :
                        action_of_creation = action
                    if action_of_creation and action.actionType() in (action.ACTIONTYPE_DELETE,) :
                        action_of_creation.setDeleted()

            if not(has_worked) :

                #----------------------------------------------------
                # 5) We're changing action type for tags
                #----------------------------------------------------

                for action in self._actions_by_branch[branch] :
                    if action.actionType() == action.ACTIONTYPE_CREATION :
                        if action.branch() == branch :
                            action.setActionType(action.ACTIONTYPE_TAG)

        # Now, action content can only change for "no tags", but "no tags" attributs doesn't change sorting order of actions
        self._actions.sort()

        for action in self._actions :
            if action.revision() not in self._revisions_to_ignore :
                branchFrom = action.branchFrom()
                revisionFrom = action.revisionFrom()
                if branchFrom != None and revisionFrom != None :
                    from_is_ok = False
                    need_change = False
                    while not(from_is_ok) :
                        from_is_ok = True
                        for from_action in self.actions_by_revision_branch(revisionFrom,branchFrom) :
                            if from_action.actionType() == from_action.ACTIONTYPE_TAG and from_action.branch() == branchFrom and from_action.revision() == revisionFrom :
                                if from_action.branchFrom() != None and from_action.revisionFrom() != None :
                                    from_is_ok = False
                                    revisionFrom = from_action.revisionFrom()
                                    branchFrom = from_action.branchFrom()
                                    need_change = True
                    if need_change :
                        action.setBranchFromNoTags(branchFrom)
                        action.setRevisionFromNoTags(revisionFrom)
                    if action.actionType() == action.ACTIONTYPE_TAG :
                        # ---- tags_by_revision_branch ----
                        self._tags_by_revision_branch[(action.revisionFromNoTags(),action.branchFromNoTags())] = self._tags_by_revision_branch.get((action.revisionFromNoTags(),action.branchFromNoTags()),[])
                        self._tags_by_revision_branch[(action.revisionFromNoTags(),action.branchFromNoTags())].append(action)
                    if action.branchFrom() != action.branchFromNoTags() or action.revisionFrom() != action.revisionFromNoTags() :
                        # ---- actions_by_revision_branch ----
                        self._actions_by_revision_branch[(action.revisionFromNoTags(),action.branchFromNoTags())] = self._actions_by_revision_branch.get((action.revisionFromNoTags(),action.branchFromNoTags()),[])
                        self._actions_by_revision_branch[(action.revisionFromNoTags(),action.branchFromNoTags())].append(action)

                self._actions_by_actionType[action.actionType()] = self._actions_by_actionType.get(action.actionType(),[])
                self._actions_by_actionType[action.actionType()].append(action)

                # usefull_revisions_by_author
                author = self._author_by_revision.get(action.revision(),None)
                if author != None :
                    self._usefull_revisions_by_author[author] = self._usefull_revisions_by_author.get(author,[])
                    self._usefull_revisions_by_author[author].append(action.revision())

        # --- revisions_nowork ---
        # --- self._branches ---

        self._branches = []
        self._revisions = self._actions_by_revision.keys()
        self._revisions.sort()
        self._revisions_nowork = []

        revisions_nowork = myset()

        for revision in self._revisions :
            for action in self._actions_by_revision[revision] :
                if action.actionType() in (action.ACTIONTYPE_CREATION,action.ACTIONTYPE_TAG,action.ACTIONTYPE_MERGE) :
                    if action.actionType() in (action.ACTIONTYPE_CREATION,action.ACTIONTYPE_MERGE) :
                        if action.revision() == revision :
                            revisions_nowork.add(revision)
                            if action.branch() not in self._branches :
                                self._branches.append(action.branch())
                    from_found = False
                    current_action = action
                    while not(from_found) :
                        if current_action.branchFrom() in self._branches :
                            from_found = True
                            revisions_nowork.add(current_action.revisionFrom())
                        else :
                            new_action = None
                            for from_action in self.actions_by_revision_branch(current_action.branchFrom(),current_action.revisionFrom()) :
                                if from_action.branch() == current_action.branchFrom() :
                                    if from_action.branchFrom() != None :
                                        new_action = from_action
                            if new_action == None :
                                # No from action at all, so we'll act as if from has been found,
                                # but in fact, no "from" revision will be added... This is the case
                                # from the trunk were the trunk isn't really
                                # created from another point. So the "from" is found, because
                                # we found there is no "from" (Are you still here?)
                                from_found = True
                            else :
                                current_action = new_action

                if action.actionType() == action.ACTIONTYPE_DELETE :
                    # only branch deletion matters, tags deletion doesn't
                    if (action.revision() == revision) and (action.branch() in self._branches):
                        revisions_nowork.add(revision)

        self._revisions_nowork = list(revisions_nowork)
        self._revisions_nowork.sort()

        # --- resolved ---

        self._resolved = True

    def branches         (self) : return self._branches
    def revisions        (self) : return self._revisions
    def revisions_nowork (self) : return self._revisions_nowork

    def actions_by_actionType (self,actionType) : return self._actions_by_actionType.get(actionType)
    def actions_by_branch (self,branch) : return self._actions_by_branch.get(branch)
    def actions_by_revision (self,revision) : return self._actions_by_revision.get(revision)
    def actions_by_revision_branch (self,revision,branch) : return self._actions_by_revision_branch.get((revision,branch),[])
    def tags_by_revision_branch (self,revision,branch) : return self._tags_by_revision_branch.get((revision,branch),[])
    def revisions_by_author (self,author) : return self._usefull_revisions_by_author.get(author,[])

if __name__ == '__main__' :
    from main import main
    main()