# cs35l
# assignment 6
# by jake greenberg-bell

# note:
# in order to verify strace i ran: strace python3 topo_order_commits.py 2>&1 | grep exec
# then i verified that none of the outputs are exec() calls which would signify the creation of a subprocess

import os, sys, zlib

class CommitNode:
    def __init__(self, commit_hash, branch, commit_num):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()
        self.branch = branch
        self.commit_num = commit_num


def topo_order_commits():
    git_path = get_git_path()  
    branches = get_all_branches(git_path)
    heads_of_branches = get_heads_of_branches(git_path, branches)
    # dictionary of commit nodes
    list_of_objects = get_all_objects(git_path)
    # dictionary of commit nodes with updated children and parents
    commit_graph = build_commit_graph(git_path, branches, list_of_objects)
    # remove commits with no parents or children
    commit_graph = trim_isolated_commits(commit_graph)
    
    start_nodes = sorted(find_start_commits(commit_graph))
    graph_edges = sorted(find_graph_edges(commit_graph, start_nodes))
    start_nodes_copy = list(start_nodes)
    topologically_sorted_graph = khans_algo(start_nodes, graph_edges)
    print_sorted_tree(topologically_sorted_graph, commit_graph, heads_of_branches, branches)

def get_heads_of_branches(git_path, branches):
    # print(git_path)
    # print(branches)
    heads_of_branches = []
    for branch in branches:
        commit = open(git_path + "/refs/heads/" + branch)
        commit = commit.read()
        heads_of_branches.append(commit.strip()) 
    return heads_of_branches

def get_graph_message(cur_hash, heads_of_branches, branches):
    branch_heads = ""
    for i in range(len(branches)):
        if heads_of_branches[i] == cur_hash:
            branch_heads += " " + branches[i]
    return branch_heads

# print a topologically sorted tree from newest to oldest commit with special rules according to spec
def print_sorted_tree(topologically_sorted_graph, commit_graph, heads_of_branches, branches):
    topologically_sorted_graph.reverse()
    previous_was_stick = False
    for i in range(len(topologically_sorted_graph)):
        cur_hash = topologically_sorted_graph[i]
        # if last commit just print hash
        if i == len(topologically_sorted_graph) - 1:
            print(cur_hash + get_graph_message(cur_hash, heads_of_branches, branches))
            return
        if(i > 0):
            prev_hash = topologically_sorted_graph[i-1]
            prev_commit_node = commit_graph[prev_hash]

        next_hash = topologically_sorted_graph[i+1]
        cur_commit_node = commit_graph[cur_hash]
        next_commit_node = commit_graph[next_hash]

        # If the next commit to be printed is not the parent of the current commit,
        # insert a “sticky end” followed by an empty line before printing the next commit.
        if next_hash not in cur_commit_node.parents:
            print(cur_hash + get_graph_message(cur_hash, heads_of_branches, branches))
            # print out parents of next commit
            parents_to_print = ""
            for parent in cur_commit_node.parents:
                # last one should include =
                parents_to_print += parent + " "
                
            print(parents_to_print + "=")
            print()
            previous_was_stick = True
        # other end of sticky
        elif previous_was_stick:
            stick_to_print = ""
            if len(cur_commit_node.children) == 0:
                print("=")
                print(cur_hash + get_graph_message(cur_hash, heads_of_branches, branches))
            else:
                added = 0
                for children in cur_commit_node.children:
                    if added == 0:
                        stick_to_print += ("=" + children + " ")
                        added = added + 1
                    else:
                        stick_to_print += (children + " ")
                        added = added + 1
                print(stick_to_print)
                print(cur_hash + get_graph_message(cur_hash, heads_of_branches, branches))
            previous_was_stick = False
        else:
            print(cur_hash + get_graph_message(cur_hash, heads_of_branches, branches))
    


# topologically returns a sorted directed acyclic graph
def khans_algo(no_parent_nodes, edges):
    # print(no_parent_nodes)
    sorted_nodes = []
    used_parent_nodes = set(no_parent_nodes)
    while len(no_parent_nodes) > 0:
        current_node = no_parent_nodes.pop()
        sorted_nodes.append(current_node)
        used_parent_nodes.add(current_node)
        # go through edges and look for links with parents to current node
        for edge in list(edges):
            parent = edge[0]
            child = edge[1]
            # delete links from current node -> other node
            if parent == current_node:
                edges.remove(edge)
                # check and see if node now has no more parent nodes
                has_link_to_parent = False
                # if edge has no other incoming edges then insert edge into no_parent_nodes
                for checking_edges in list(edges):
                    # if a link has a child which is the node don't delete
                    if checking_edges[1] == child:
                        has_link_to_parent = True
                if (has_link_to_parent == False) and (child not in used_parent_nodes):
                    no_parent_nodes.append(child)
    return sorted_nodes


# returns a set of tuple (parent hash, child hash) unordered pairs
def find_graph_edges(commit_graph, start_nodes):
    graph_edges = []
    node_stack = set()
    for node in start_nodes:
        node_stack.add(node)
    while len(node_stack) != 0:
        cur_node = commit_graph[node_stack.pop()]
        for child in cur_node.children:
            graph_tuple = (cur_node.commit_hash, child)
            if graph_tuple not in graph_edges:
                graph_edges.append(graph_tuple)
            node_stack.add(child)
    return graph_edges

# returns a list of all commit hashes with no children
def find_start_commits(commit_graph):
    start_commits = []
    for commit_hash, v in commit_graph.items():
        commit_node = commit_graph[commit_hash]
        if len(commit_node.parents) == 0 and len(commit_node.children) != 0:
            start_commits.append(commit_hash)
    return start_commits

# removes commits from list_of_objects with no parents or children
def trim_isolated_commits(commit_graph):
    to_delete = []
    for commit_hash, v in commit_graph.items():
        commit_node = commit_graph[commit_hash]
        if len(commit_node.parents) == 0 and len(commit_node.children) == 0:
            to_delete.append(commit_hash)
    for key in to_delete:
        del commit_graph[key]
    return commit_graph

# tester function to determine progress
def print_all_commit_test(list_of_objects):
    for commit_hash, v in list_of_objects.items():
        commit_node = list_of_objects[commit_hash]
        print("")
        print("Commit hash: ")
        print(commit_node.commit_hash)
        print("Parents: ")
        print(commit_node.parents)
        print("Children: ")
        print(commit_node.children)
        print("Commit number: ")
        print(commit_node.commit_num)

def build_commit_graph(git_path, branches, list_of_objects):
    commits = {}
    branches_count = 0
    for x in branches:
        # find head of branch
        full_path = git_path + "/refs/heads/" + x
        full_path = open(full_path)
        branch_head_hash = full_path.read().strip()
        try:
            cur_node = list_of_objects[branch_head_hash]
        except:
            continue
        # create stack of parent hashes to do DFS
        parent_stack = [cur_node.commit_hash]
        while len(parent_stack) != 0:
            cur_node = list_of_objects[parent_stack.pop()]
            # add parents of cur_node to parent_stack
            for parent in cur_node.parents:
                parent_stack.append(parent)
            # add cur node as children to parents
            for parent in cur_node.parents:
                parent_node = list_of_objects[parent]
                parent_node.children.add(cur_node.commit_hash)
    return list_of_objects



def get_git_path():
    current_wd = os.getcwd()
    git_path = "false"
    while git_path == "false":
        # looks within current directory for .git
        try:
            current_dirs_and_files = os.listdir(current_wd)
        except:
            print("Not inside a Git repository", file = sys.stderr)
            break
        if '.git' in current_dirs_and_files:
            return current_wd + '/.git'
        else:
            # if it's not there it searche the directory above
            last_backslash = -1
            # if it just searched root directory to no avail exit with status 1
            if current_wd == "/":
                    print("Not inside a Git repository", file = sys.stderr)
                    sys.exit(1)    
            for element in range(0, len(current_wd)):
                if current_wd[element] == '/':
                    last_backslash = element

def get_all_branches(path):
    path_to_heads = path + "/refs/heads"
    dir_ref_heads = os.listdir(path_to_heads)
    to_check = dir_ref_heads
    branches = []
    # check for directories
    while len(to_check) > 0:
        check_path = to_check.pop()
        if os.path.isdir(path_to_heads + "/" + check_path):
            to_add = os.listdir(path_to_heads + "/" + check_path)
            for x in to_add:
                to_check.append(check_path + "/" + x)
        else:
            branches.append(check_path)
    return(branches)



    return(dir_ref_heads)

def get_all_objects(path):
    path_to_objects = path + "/objects/"
    all_object_directories = os.listdir(path_to_objects)
    all_object_arrays = {}
    # perform on each object
    for x in all_object_directories:
        obj_path_arr = os.listdir(path_to_objects + x)
        path_prefix = path_to_objects + x
        # for each file in directory
        for file_var in obj_path_arr:
            # open and decode file
            original_path = file_var
            file_var = open(path_prefix + "/" + file_var, "rb")
            binary_blob = file_var.read()
            decompress_blob = zlib.decompress(binary_blob).decode('utf-8', "ignore")
            listed_decompress_blob = decompress_blob.split()
            # only keep the commit objects
            if listed_decompress_blob[0] == "commit":
                last_backslash = path_prefix.rfind('/')
                commit_hash = path_prefix[last_backslash + 1:] + original_path
                branch = listed_decompress_blob[len(listed_decompress_blob) - 2]
                commit_num = listed_decompress_blob[len(listed_decompress_blob) - 1]
                # create and add a CommitNode to list
                new_commit_node = CommitNode(commit_hash, branch, commit_num)
                # get the parents
                parents = []
                previous_was_parent = False
                for prop in listed_decompress_blob:
                    if previous_was_parent:
                        parents.append(prop)
                        previous_was_parent = False
                    elif prop == "parent":
                        previous_was_parent = True
                # add the parents to CommitNode
                for parent in parents:
                    new_commit_node.parents.add(parent)
                all_object_arrays[commit_hash] = new_commit_node
    return all_object_arrays
    
    

        
if __name__ == '__main__':
    topo_order_commits()
