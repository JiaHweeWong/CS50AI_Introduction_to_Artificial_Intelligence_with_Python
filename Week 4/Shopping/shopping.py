import csv
import sys
import numpy as np
import calendar

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    int_var = {
        "Administrative", "Informational", "ProductRelated",
        "Month", "OperatingSystems", "Browser", "Region",
        "TrafficType", "VisitorType", "Weekend"
    }

    float_var = {
        "Administrative_Duration", "Informational_Duration", 
        "ProductRelated_Duration", "BounceRates", "ExitRates",
        "PageValues", "SpecialDay"
    }
    
    month_dict = {
        "Jan" : 0,
        "Feb" : 1,
        "Mar" : 2,
        "Apr" : 3,
        "May" : 4,
        "June" : 5,
        "Jul" : 6,
        "Aug" : 7,
        "Sep" : 8,
        "Oct" : 9,
        "Nov" : 10,
        "Dec" : 11
    }

    weekend_dict = {
        "FALSE" : 0,
        "TRUE" : 1
    }

    labels_dict = {
        "FALSE" : 0,
        "TRUE" : 1
    }

    evidence = []
    labels = []

    with open(filename) as f:
        reader = list(csv.DictReader(f))

        for row in reader: # for each row
            # Convert Month to int
            row['Month'] = month_dict[row['Month']]

            # Convert VisitorType to int
            row['VisitorType'] = 1 if row['VisitorType'] == 'Returning_Visitor' else 0

            # Convert Weekend to int
            row['Weekend'] = weekend_dict[row['Weekend']]

            # Convert all int var into int
            for var in int_var:
                row[var] = int(row[var])

            # Convert all float var into float
            for var in float_var:
                row[var] = float(row[var])
            # append row_evidence to evidence
            evidence.append(list(row.values())[:-1])
            labels.append(labels_dict[row['Revenue']])
        return (evidence, labels)

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_pos = 0 # true positive
    true_neg = 0 # true negative
    
    false_pos = 0 # false positive
    false_neg = 0 # false negative

    for y_true, y_pred in zip(labels, predictions):
        if y_true == y_pred: # if prediction is correct
            if y_true == 1: # if label is pos
                true_pos += 1 # true pos + 1
            elif y_true == 0: # if label is neg
                true_neg += 1 # true neg + 1
        else:
            if y_pred == 1: # if pred is false pos
                false_pos += 1 # false pos + 1
            elif y_pred == 0: # if pred is false neg
                false_neg += 1 # false neg + 1

    sensitivity = true_pos / (true_pos + false_neg) # sensitivity
    specificity = true_neg / (true_neg + false_neg) # specificity
    return (sensitivity, specificity)
 


if __name__ == "__main__":
    main()
