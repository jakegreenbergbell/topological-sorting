
# Topological Sort
Creates topological sorting of git's acyclic directed graph.

## Running

Simply add the script into an existing git repository, navigate to your project, and run the following in your shell terminal:

```
$ python3 topo_order_commits.py
```

## Output

The topo_order_commits.py script imitates the functionality of:
```
$ git log
```
It does this by taking the git repository, which contains an acyclic directed graph of the commits and looking at the related child and parent nodes to find an ordering of this graph which represents the topological ordering.
