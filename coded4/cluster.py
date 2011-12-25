'''
Algorithms for clustering commits
'''

def group_by_contributors(commit_history):
    ''' Goes through commit history and groups commits by their authors.
    @param commit_history: List of Commit tuples
    @return: Dictionary mapping author names to lists of Commit tuples
    '''
    commits = {}
    for commit in commit_history:
        commit_list = commits.setdefault(commit.author, [])
        commit_list.append(commit)

    return commits

def cluster_commits(grouped_commits, cluster_algo, epsilon):
    ''' Clusters commits for every contributor in given dictionary. 
    @param grouped_commits: Dictionary mapping contributor names to lists of Commit tuples
    @param cluster_algo: Name of clustering algorithm
    @param epsilon: Temporal distance for the epsilon-neighborhood
    @return: Dictionary mapping author names to lists of coding sessions
    '''
    cluster_func = globals().get(cluster_algo + '_clustering')
    if not cluster_func:
        raise ValueError, "Unknown clustering algorithm '%s'" % cluster_algo

    clustered = {}
    for author, commits in grouped_commits.iteritems():
        sessions = cluster_func(commits, epsilon)
        clustered[author] = sessions

    return clustered


## Algorithms

def simple_clustering(commits, epsilon):
    ''' Divides list of commits into clusters (coding sessions) using simple clustering.
    @param epsilon: Maximum time interval between commit in single session
    @return: List of lists of Commit tuples
    '''
    sessions = []

    session = []
    commit_iter = iter(commits)
    while True:
        commit = next(commit_iter, None)
        if not commit:
            if session: sessions.append(session)
            break

        # if interval between commits is too long, assume end of session
        if session and last_commit_time - commit.time > epsilon:
            sessions.append(session)
            session = []
        session.append(commit)
        last_commit_time = commit.time

    return sessions
    