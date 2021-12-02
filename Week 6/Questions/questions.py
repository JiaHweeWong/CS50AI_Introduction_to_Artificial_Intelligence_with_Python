import nltk
import sys
import os
import string
import re
import math


FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    list_of_txt_filenames = os.listdir(directory)
    full_dict = {}
    for filename in list_of_txt_filenames:
        full_txt_path = os.path.join(directory, filename)
        f = open(full_txt_path, "r", encoding='utf8')
        full_dict[filename] = f.read()
        f.close()
    return full_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokens = nltk.word_tokenize(document)
    new_tokens = []
    punctuations = string.punctuation
    stopwords = nltk.corpus.stopwords.words("english")
    for token in tokens:
        new_token = token
        if new_token in stopwords:
            continue
        new_token = new_token.translate(str.maketrans('', '', punctuations))
        if (new_token == "") | (new_token in stopwords):
            continue
        else:
            new_token = new_token.lower()
            new_tokens.append(new_token)
    return new_tokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    def get_idf(n, doc_freq):
        frac = n/doc_freq
        idf = math.log(frac)
        return idf
 
    n = len(documents)
    doc_freq_dict = {}
    idfs_dict = {}

    for doc in documents.keys():
        list_of_unique_words_in_doc = list(set(documents[doc]))
        for word in list_of_unique_words_in_doc:
            if word in doc_freq_dict:
                doc_freq_dict[word] += 1
            else:
                doc_freq_dict[word] = 1
                idfs_dict[word] = 0

    for word in doc_freq_dict.keys():
        doc_freq = doc_freq_dict[word]
        idfs_val = get_idf(n, doc_freq)
        idfs_dict[word] = idfs_val

    return idfs_dict

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidf_dict = {}
    ranked_list = []
    for filename, list_of_words in files.items():
        tfidf_dict[filename] = 0
        for query_word in query:
            idf_score = idfs[query_word]
            tf_score = list_of_words.count(query_word)
            tfidf_score = idf_score * tf_score
            tfidf_dict[filename] += tfidf_score

    while len(ranked_list) != n:
        highest_tfidf_score = 0
        file_w_highest_tfidf_score = ''
        set_of_ranked_files = set(ranked_list)
        for filename, curr_tfidf_score in tfidf_dict.items():
            if filename in set_of_ranked_files:
                continue
            if curr_tfidf_score > highest_tfidf_score:
                highest_tfidf_score = curr_tfidf_score
                file_w_highest_tfidf_score = filename
        ranked_list.append(file_w_highest_tfidf_score)
    return ranked_list


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    def get_query_term_density(query, sentences, sentence):
        list_of_words = sentences[sentence]
        sentence_length = len(list_of_words)
        query_words_count = 0
        for word in list_of_words:
            if word in query:
                query_words_count += 1
        density = query_words_count / sentence_length
        return density

    sentences_mwm_dict = {}
    ranked_list = []

    for sentence, list_of_words in sentences.items():
        set_of_words_in_sentence = set(list_of_words)
        for query_word in query:
            if query_word in set_of_words_in_sentence:
                idf_score = idfs[query_word]
                if sentence in sentences_mwm_dict:
                    sentences_mwm_dict[sentence] += idf_score
                elif sentence not in sentences_mwm_dict:
                    sentences_mwm_dict[sentence] = idf_score
    
    while len(ranked_list) != n:
        highest_mwm_score = 0
        sentence_with_best_idf_score = ''
        set_of_ranked_sentences = set(ranked_list)
        for sentence, curr_mwm_score in sentences_mwm_dict.items():
            if sentence in set_of_ranked_sentences:
                continue
            if curr_mwm_score > highest_mwm_score:
                highest_mwm_score = curr_mwm_score
                sentence_with_best_idf_score = sentence
            elif curr_mwm_score == highest_mwm_score:
                curr_sentence_density = get_query_term_density(query, sentences, sentence)
                best_sentence_density = get_query_term_density(query, sentences, sentence_with_best_idf_score)
                if curr_sentence_density > best_sentence_density:
                    highest_mwm_score = curr_mwm_score
                    sentence_with_best_idf_score = sentence
        ranked_list.append(sentence_with_best_idf_score)
    
    return ranked_list


if __name__ == "__main__":
    main()
