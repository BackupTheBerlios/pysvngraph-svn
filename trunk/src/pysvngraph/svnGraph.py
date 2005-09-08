#!/usr/bin/env python
# coding: iso-8859-1

from svnRepository import myset

class svnGraph :
    def __init__(self,repository,renderer,configuration) :
        self._repository = repository
        self._renderer = renderer
        self._configuration = configuration

        self._compact = False
        self._less_columns = False
        self._columns = None

    def compact(self,param=None) :
        if param != None :
            self._compact = param
        return self._compact

    def less_columns(self,param=None) :
        if param != None :
            self._less_columns = param
        return self._less_columns

    def columns(self,param=None) :
        if param != None :
            self._columns = param
        return self._columns

    def render(self) :
        self._repository.resolv()
        branches = self._repository.branches()
        
        print "--------"
        for branche in branches :
            print "%s" % (branche,)
        print "--------"
            
        if self._columns == None :
            self._columns = branches
        else :
            columns = []
            for column in self._columns :
                if column in branches :
                   columns.append(column)
            self._columns = columns
        pos_branch = {}
        index = 0
        for branch in self._columns :
            pos_branch[branch] = index
            index += 1
        index = 0

        # --------

        graph_size_border = int(self._configuration['graph_size_border'])

        graph_size_width_column = int(self._configuration['graph_size_width_column'])
        graph_size_height_atorevision = int(self._configuration['graph_size_height_atorevision'])

        graph_size_width_label = int(self._configuration['graph_size_width_label'])
        graph_size_height_label = int(self._configuration['graph_size_height_label'])

        graph_size_offset_label_left = int(self._configuration['graph_size_offset_label_left'])
        graph_size_offset_label_top = int(self._configuration['graph_size_offset_label_top'])

        graph_size_localoffset_merge_from_center = int(self._configuration['graph_size_localoffset_merge_from_center'])

        graph_size_height_revision = graph_size_height_label
        graph_size_width_revision = graph_size_height_revision

        graph_size_localoffset_label_left = (graph_size_width_column-graph_size_width_label)/2
        graph_size_localoffset_label_top = (graph_size_height_atorevision-graph_size_height_label)/2

        graph_size_localoffset_end_label_left = graph_size_width_column-graph_size_localoffset_label_left
        graph_size_localoffset_end_label_top = graph_size_height_atorevision-graph_size_localoffset_label_top

        graph_size_localoffset_rebranche_left = graph_size_width_column
        graph_size_localoffset_rebranche_top = int(self._configuration['graph_size_localoffset_rebranche_top'])

        graph_size_offset_revision_left = int(self._configuration['graph_size_offset_revision_left'])
        graph_size_localoffset_revision_top = (graph_size_height_atorevision-graph_size_height_revision)/2
        graph_size_localoffset_end_revision_top = graph_size_height_atorevision-graph_size_localoffset_revision_top

        graph_size_localoffset_middle_label_left = (graph_size_width_column/2)
        graph_size_localoffset_middle_label_top = (graph_size_height_atorevision/2)

        graph_size_localoffset_merge_left = graph_size_localoffset_middle_label_left-graph_size_localoffset_merge_from_center
        graph_size_localoffset_merge_right = graph_size_localoffset_middle_label_left+graph_size_localoffset_merge_from_center

        graph_size_localoffset_mergeline_vspace = int(self._configuration['graph_size_localoffset_mergeline_vspace'])
        graph_size_localoffset_mergeline_left = int(self._configuration['graph_size_localoffset_mergeline_left'])

        graph_size_localoffset_mergebar_top = graph_size_localoffset_label_top-graph_size_localoffset_mergeline_vspace

        graph_size_localoffset_mergebar_left = int(self._configuration['graph_size_localoffset_mergebar_left'])
        graph_size_localoffset_mergebar_right = graph_size_width_column-graph_size_localoffset_mergebar_left

        graph_option_draw_deleted_tags = bool(int(self._configuration['graph_option_draw_deleted_tags']))
        graph_option_draw_tags = bool(int(self._configuration['graph_option_draw_tags']))
        graph_option_draw_all_work = bool(int(self._configuration['graph_option_draw_all_work']))
        graph_option_highlight_authors = self._configuration['graph_option_highlight_authors'].split(',')

        graph_option_write_text = bool(int(self._configuration['graph_option_write_text']))
        graph_option_draw_revision = bool(int(self._configuration['graph_option_draw_revision']))
        
        graph_fit_to_page = bool(int(self._configuration['graph_fit_to_page']))

        # --------

        # [AFaire] : use configuration file

        self._renderer.set_param('default_border',graph_size_border)
        self._renderer.set_param('no_text',not(graph_option_write_text))
        if graph_fit_to_page :
            self._renderer.set_fit_to_size()
        self._renderer.start_drawing()

        index_revision_list = {}
        index_branch_list = {}

        index_branch = 0

        last_index_revision_by_branch = {}

        for branch in self._columns :
            index_branch_list[branch] = index_branch
            self._renderer.draw_rect(
                index_branch*graph_size_width_column+graph_size_localoffset_label_left+graph_size_offset_label_left,
                graph_size_localoffset_label_top,
                index_branch*graph_size_width_column+graph_size_localoffset_end_label_left+graph_size_offset_label_left,
                graph_size_localoffset_end_label_top,
                color=self._renderer.Color(0xff,0x88,0x88),
                fillcolor=self._renderer.Color(0xff,0xcc,0xcc),
                text=branch.split('/')[-1]
                )
            index_branch += 1
            last_index_revision_by_branch[branch] = None

        index_revision = 0

        if graph_option_draw_all_work :
            revisions_to_draw = self._repository.revisions()
        else :
            revisions_to_draw = self._repository.revisions_nowork()

        latest_revsion_by_branch = {}
        for branch in self._columns :
            revision = 0
            for action in self._repository.actions_by_branch(branch) :
                if action.branch() == branch and revision < action.revision() :
                    revision = action.revision()
            latest_revsion_by_branch[branch] = revision
            if revision not in revisions_to_draw :
                revisions_to_draw.append(revision)

        revisions_to_highlight = myset()
        if graph_option_highlight_authors != None :
            for author in graph_option_highlight_authors :
                for revision in self._repository.revisions_by_author(author) :
                    revisions_to_highlight.add(revision)
                    if revision not in revisions_to_draw :
                        revisions_to_draw.append(revision)

        revisions_to_draw.sort()
        for revision in revisions_to_draw :
            print "--%d--" % (revision,)
            index_revision_list[revision] = index_revision
            index_branch = 0

            index_revision_base = index_revision
            index_revision_max = index_revision_base

            drawn_something_for_that_revision = False
            for branch in self._columns :
                index_revision = index_revision_base
                action_to_draw = False
                action_must_draw = False
                action_may_draw = False
                tagslist_to_draw = []
                action_text = ""
                actionfrom = None
                mergefroms = []

                action_drawn = False
                action_delete_branch = False
                action_creation_is_now_deleted = False

                for action in self._repository.actions_by_revision_branch(revision,branch) :
                    print "  [%s]" % (action,)
                    if action.branch() == branch and action.revision() == revision :
                        if action.actionType() == action.ACTIONTYPE_CREATION :
                            action_to_draw = True
                            action_must_draw = True
                            action_text += "C"
                            if action.deleted() :
                                action_creation_is_now_deleted = True
                            if action.branchFrom() != None and action.revisionFrom() != None :
                                if action.branchFromNoTags() in self._columns :
                                    actionfrom = (action.branchFromNoTags(),action.revisionFromNoTags())
                        elif action.actionType() == action.ACTIONTYPE_WORK :
                            action_may_draw = True
                            action_text += "W"
                        elif action.actionType() == action.ACTIONTYPE_TAG :
                            action_text += "T"
                        elif action.actionType() == action.ACTIONTYPE_DELETE :
                            action_to_draw = True
                            action_must_draw = True
                            action_delete_branch = True
                            action_text += "D"
                        elif action.actionType() == action.ACTIONTYPE_MERGE :
                            action_text += "M"
                            if action.branchFrom() != None and action.revisionFrom() != None :
                                if action.branchFromNoTags() in self._columns :
                                    action_to_draw = True
                                    action_must_draw = True
                                    mergefroms.append((action.branchFromNoTags(),action.revisionFromNoTags()))
                        if latest_revsion_by_branch[branch] == revision :
                            action_to_draw = True
                            action_must_draw = True
                            action_text += "[L]"
                    elif action.branchFromNoTags() == branch and action.revisionFromNoTags() == revision :
                        if action.branch() in self._columns :
                            action_to_draw = True
                            # action_must_draw = True
                for tag_action in self._repository.tags_by_revision_branch(revision,branch) :
                    # print "*** %s ***" % (tag_action,)
                    if graph_option_draw_tags :
                        if not(tag_action.deleted()) or graph_option_draw_deleted_tags :
                            tagslist_to_draw.append((tag_action.revision(),tag_action.branch(),tag_action.deleted()))
                if action_may_draw and ((revision in revisions_to_highlight) or graph_option_draw_all_work) :
                    action_to_draw = True
                if action_to_draw and (action_must_draw or len(tagslist_to_draw)<=0) :
                    draw_rect_params = {}
                    if action_delete_branch :
                        draw_rect_params['fillcolor']=self._renderer.Color('red')
                    if revision in revisions_to_highlight :
                        draw_rect_params['fillcolor']=self._renderer.Color('uglybrown')
                    if action_creation_is_now_deleted :
                        draw_rect_params['fillcolor']=self._renderer.Color('lightblue')
                    self._renderer.draw_rect(
                        index_branch*graph_size_width_column          +  graph_size_localoffset_label_left      +  graph_size_offset_label_left,
                        index_revision*graph_size_height_atorevision  +  graph_size_localoffset_label_top       +  graph_size_offset_label_top,
                        index_branch*graph_size_width_column          +  graph_size_localoffset_end_label_left  +  graph_size_offset_label_left,
                        index_revision*graph_size_height_atorevision  +  graph_size_localoffset_end_label_top   +  graph_size_offset_label_top,
                        text=action_text+" %d"%(revision,),
                        **draw_rect_params
                        )
                    action_drawn = True
                    drawn_something_for_that_revision = True
                    localoffset_label_top = graph_size_localoffset_label_top
                    if len(mergefroms)!=0 :
                        localoffset_label_top = graph_size_localoffset_mergebar_top
                    if actionfrom :
                        if index_branch_list[actionfrom[0]] > index_branch_list[branch] :
                            self._renderer.draw_line(
                                index_branch_list[actionfrom[0]]*graph_size_width_column          +  graph_size_localoffset_label_left         +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top   +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top   +  graph_size_offset_label_top,
                                )
                            self._renderer.draw_line(
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top   +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision                      +  localoffset_label_top                     +  graph_size_offset_label_top,
                                )
                        elif index_branch_list[actionfrom[0]] < index_branch_list[branch] :
                            self._renderer.draw_line(
                                index_branch_list[actionfrom[0]]*graph_size_width_column          +  graph_size_localoffset_end_label_left     +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top   +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top   +  graph_size_offset_label_top,
                                )
                            self._renderer.draw_line(
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top   +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision                      +  localoffset_label_top                     +  graph_size_offset_label_top,
                                )
                        elif index_branch_list[actionfrom[0]] == index_branch_list[branch] :
                            self._renderer.draw_line(
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_end_label_left    +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top  +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_rebranche_left    +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top  +  graph_size_offset_label_top,
                                )
                            self._renderer.draw_line(
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_rebranche_left    +  graph_size_offset_label_left,
                                index_revision_list[actionfrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_middle_label_top  +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column                              +  graph_size_localoffset_rebranche_left    +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision                      +  graph_size_localoffset_rebranche_top     +  graph_size_offset_label_top,
                                )
                            self._renderer.draw_line(
                                index_branch*graph_size_width_column          +  graph_size_localoffset_rebranche_left     +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision  +  graph_size_localoffset_rebranche_top      +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column          +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision  +  graph_size_localoffset_rebranche_top      +  graph_size_offset_label_top,
                                )
                            self._renderer.draw_line(
                                index_branch*graph_size_width_column          +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision  +  graph_size_localoffset_rebranche_top      +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column          +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision  +  localoffset_label_top                     +  graph_size_offset_label_top,
                                )
                    else :
                        # or else, we're just comming from the previous rectangle from
                        # the same branch...

                        # if the current branch has a last revision
                        if last_index_revision_by_branch[branch] != None :
                            # So we draw only a line only if there is a previous
                            # rectangle to connect to...

                            last_index_revision = last_index_revision_by_branch[branch]
                            self._renderer.draw_line(
                                index_branch*graph_size_width_column               +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                last_index_revision*graph_size_height_atorevision  +  graph_size_localoffset_end_label_top      +  graph_size_offset_label_top,
                                index_branch*graph_size_width_column               +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                                index_revision*graph_size_height_atorevision       +  localoffset_label_top                     +  graph_size_offset_label_top,
                                )
                    # So now, the last revision for this branch is the current one...
                    last_index_revision_by_branch[branch] = index_revision
                    for mergefrom in mergefroms :
                        if index_branch_list[mergefrom[0]] > index_branch_list[branch] :
                            localoffset_merge_init = graph_size_localoffset_merge_left
                            localoffset_merge_end = graph_size_localoffset_merge_right
                            localoffset_mergeline_left = graph_size_localoffset_mergeline_left
                        elif index_branch_list[mergefrom[0]] < index_branch_list[branch] :
                            localoffset_merge_init = graph_size_localoffset_merge_right
                            localoffset_merge_end = graph_size_localoffset_merge_left
                            localoffset_mergeline_left = graph_size_localoffset_mergeline_left+graph_size_width_column
                        else :
                            localoffset_merge_init = graph_size_localoffset_merge_right
                            localoffset_merge_end = graph_size_localoffset_merge_right
                            localoffset_mergeline_left = graph_size_localoffset_mergeline_left+graph_size_width_column
                        self._renderer.draw_line(
                            index_branch_list[mergefrom[0]]*graph_size_width_column          +  localoffset_merge_init                                                        +  graph_size_offset_label_left,
                            index_revision_list[mergefrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_end_label_top                                          +  graph_size_offset_label_top,
                            index_branch_list[mergefrom[0]]*graph_size_width_column          +  localoffset_merge_init                                                        +  graph_size_offset_label_left,
                            index_revision_list[mergefrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace  +  graph_size_offset_label_top,
                            )
                        self._renderer.draw_line(
                            index_branch_list[mergefrom[0]]*graph_size_width_column          +  localoffset_merge_init                                                        +  graph_size_offset_label_left,
                            index_revision_list[mergefrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace  +  graph_size_offset_label_top,
                            index_branch_list[mergefrom[0]]*graph_size_width_column          +  localoffset_mergeline_left                                                    +  graph_size_offset_label_left,
                            index_revision_list[mergefrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace  +  graph_size_offset_label_top,
                            )
                        self._renderer.draw_line(
                            index_branch_list[mergefrom[0]]*graph_size_width_column          +  localoffset_mergeline_left                                                    +  graph_size_offset_label_left,
                            index_revision_list[mergefrom[1]]*graph_size_height_atorevision  +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace  +  graph_size_offset_label_top,
                            index_branch_list[mergefrom[0]]*graph_size_width_column          +  localoffset_mergeline_left                                                    +  graph_size_offset_label_left,
                            (index_revision-1)*graph_size_height_atorevision                 +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace  +  graph_size_offset_label_top,
                            )
                        self._renderer.draw_line(
                            index_branch_list[mergefrom[0]]*graph_size_width_column  +  localoffset_mergeline_left                                                   +  graph_size_offset_label_left,
                            (index_revision-1)*graph_size_height_atorevision         +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace +  graph_size_offset_label_top,
                            index_branch*graph_size_width_column                     +  localoffset_merge_end                                                        +  graph_size_offset_label_left,
                            (index_revision-1)*graph_size_height_atorevision         +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace +  graph_size_offset_label_top,
                            )
                        self._renderer.draw_line(
                            index_branch*graph_size_width_column          +  localoffset_merge_end                                                        +  graph_size_offset_label_left,
                            (index_revision-1)*graph_size_height_atorevision +  graph_size_localoffset_end_label_top+graph_size_localoffset_mergeline_vspace  +  graph_size_offset_label_top,
                            index_branch*graph_size_width_column          +  localoffset_merge_end                                                        +  graph_size_offset_label_left,
                            index_revision*graph_size_height_atorevision  +  graph_size_localoffset_mergebar_top                                          +  graph_size_offset_label_top,
                            )
                        self._renderer.draw_line(
                            index_branch*graph_size_width_column          +  graph_size_localoffset_mergebar_left   +  graph_size_offset_label_left,
                            index_revision*graph_size_height_atorevision  +  graph_size_localoffset_mergebar_top    +  graph_size_offset_label_top,
                            index_branch*graph_size_width_column          +  graph_size_localoffset_mergebar_right  +  graph_size_offset_label_left,
                            index_revision*graph_size_height_atorevision  +  graph_size_localoffset_mergebar_top    +  graph_size_offset_label_top,
                            )
                        self._renderer.draw_line(
                            index_branch*graph_size_width_column          +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                            index_revision*graph_size_height_atorevision  +  graph_size_localoffset_mergebar_top       +  graph_size_offset_label_top,
                            index_branch*graph_size_width_column          +  graph_size_localoffset_middle_label_left  +  graph_size_offset_label_left,
                            index_revision*graph_size_height_atorevision  +  graph_size_localoffset_label_top          +  graph_size_offset_label_top,
                            )

                for taginfo in tagslist_to_draw :
                    if action_drawn :
                        index_revision += 1
                    draw_rect_params = {}
                    if taginfo[2] :
                        draw_rect_params['fillcolor']=self._renderer.Color('lightblue')
                    if revision in revisions_to_highlight :
                        draw_rect_params['fillcolor']=self._renderer.Color('uglybrown')
                    draw_rect_params['color']=self._renderer.Color('red')
                    self._renderer.draw_rect(
                        index_branch*graph_size_width_column+graph_size_localoffset_label_left+graph_size_offset_label_left,
                        index_revision*graph_size_height_atorevision+graph_size_localoffset_label_top+graph_size_offset_label_top,
                        index_branch*graph_size_width_column+graph_size_localoffset_end_label_left+graph_size_offset_label_left,
                        index_revision*graph_size_height_atorevision+graph_size_localoffset_end_label_top+graph_size_offset_label_top,
                        text="T %d : %s" % (taginfo[0],taginfo[1].split('/')[-1]),
                        **draw_rect_params
                        )
                    action_drawn = True
                    drawn_something_for_that_revision = True
                    if last_index_revision_by_branch[branch] != None :
                        last_index_revision = last_index_revision_by_branch[branch]
                        self._renderer.draw_line(
                            index_branch*graph_size_width_column+graph_size_localoffset_middle_label_left+graph_size_offset_label_left,
                            last_index_revision*graph_size_height_atorevision+graph_size_localoffset_end_label_top+graph_size_offset_label_top,
                            index_branch*graph_size_width_column+graph_size_localoffset_middle_label_left+graph_size_offset_label_left,
                            index_revision*graph_size_height_atorevision+graph_size_localoffset_label_top+graph_size_offset_label_top,
                            )
                    last_index_revision_by_branch[branch] = index_revision
                index_branch += 1
                index_revision_max = max(index_revision,index_revision_max)

            if drawn_something_for_that_revision :
                index_revision=index_revision_max+1
                if graph_option_draw_revision :
                    self._renderer.draw_rect(
                        graph_size_offset_revision_left,
                        index_revision_base*graph_size_height_atorevision+graph_size_localoffset_revision_top+graph_size_offset_label_top,
                        graph_size_offset_revision_left+graph_size_width_revision,
                        index_revision_base*graph_size_height_atorevision+graph_size_localoffset_end_revision_top+graph_size_offset_label_top,
                        fillcolor=self._renderer.Color('lightyellow'),
                        text="%d"%(revision,)
                        )
                    self._renderer.draw_line(
                        0,
                        index_revision*graph_size_height_atorevision+graph_size_offset_label_top,
                        len(self._columns)*graph_size_width_column+graph_size_offset_label_left,
                        index_revision*graph_size_height_atorevision+graph_size_offset_label_top,
                        color=self._renderer.Color(0xdd,0xdd,0xdd),
                        z=-1
                        )

        self._renderer.stop_drawing()

if __name__ == '__main__' :
    from main import main
    main()