import os
import random
import re
import sys
import numpy as np
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.

    corpus: Python dictionary mapping a page name to a set of all pages linked to by that page
    page: string representing which page the random surfer is currently on
    damping_factor: floating point number representing the damping factor to be used when generating the probabiliteies
    """
    one_minus_damp = 1 - damping_factor
    set_of_linked_pages = corpus[page]
    output_dict = {}
    # Case 1: current page has no outgoing links
    if len(set_of_linked_pages) == 0:
        proba = 1/len(corpus)
        for key in corpus.keys():
            output_dict[key] = proba

    # Case 2: Normal Scenario
    else:
        base_proba = one_minus_damp/len(corpus)
        linked_proba = damping_factor/len(set_of_linked_pages)
        for key in corpus.keys():
            output_dict[key] = base_proba
            if key in set_of_linked_pages:
                output_dict[key] += linked_proba
        
    return output_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    list_of_pages = list(corpus.keys())
    # Initialization
    curr_page = random.choice(list_of_pages)
    output_dict = {}
    for page in list_of_pages:
        output_dict[page] = 0
    output_dict[curr_page] += 1
    # Sampling Using transition_model
    counter = 0
    while counter < n:
        counter += 1
        distribution = transition_model(corpus,curr_page,damping_factor)
        list_of_proba = distribution.values()
        next_page = random.choices(list_of_pages, weights=list_of_proba)[0]
        output_dict[next_page] += 1
        curr_page = next_page

    for key in output_dict.keys():
        output_dict[key] = output_dict[key]/n
    
    return output_dict

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """         
    # Initialization
    N = len(corpus.keys())
    curr_dict = {} # key: page, value: page rank of the key
    next_dict = {} # key: page, value: page rank of the key
    for key in corpus.keys():
        curr_dict[key] = 1/N
        next_dict[key] = 1

    # Iteration
    threshold = 0.001
    error = max(abs(np.array(list(next_dict.values())) - np.array(list(curr_dict.values()))))
    iter_counter = 0
    case1 = (1-damping_factor)/N
    while ((error > threshold) | (abs(sum(next_dict.values())-1) >= 0.001)):
        iter_counter += 1
        if iter_counter != 1:
            curr_dict = next_dict
        for page_p in curr_dict.keys():
            case2=0
            for page_i, linked_pages in corpus.items():
                if len(linked_pages) == 0:
                    linked_pages = corpus.keys()
                if page_p not in linked_pages: # if page_i is not linked to page_p, continue
                    continue
                elif page_p in linked_pages: # if page_i links to page_p
                    pr_i = curr_dict[page_i] # page rank of page i
                    numlinks = len(linked_pages) # number of links in page i
                    frac = pr_i/numlinks
                    case2 += frac # summation of case 2
            case2 = damping_factor * case2 # formula for case 2
            pr_p = case1+case2 # page rank formula
            next_dict[page_p] = pr_p
        error = max(abs(np.array(list(next_dict.values())) - np.array(list(curr_dict.values()))))
    return next_dict

if __name__ == "__main__":
    main()
