import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },
    
    # Conditional Probabilities for having the trait given number of genes
    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

mutate_prob = PROBS['mutation']

COND_PROB_TABLE = {
    # If child has 0 gene 
    0 : {
        # Dad 0 gene, Mum 0 gene
        (0,0) : (1-mutate_prob) ** 2, # 0.9801
        # Dad 0 gene, Mum 1 gene
        (0,1) : (1-mutate_prob) * ((0.5*(1-mutate_prob)) + (0.5*mutate_prob)), # 0.495
        # Dad 0 gene, Mum 2 genes
        (0,2) : (1-mutate_prob) * mutate_prob, # 0.0099
        # Dad 1 gene, Mum 0 gene
        (1,0) : (1-mutate_prob) * ((0.5*(1-mutate_prob)) + (0.5*mutate_prob)), # 0.495
        # Dad 1 gene, Mum 1 gene
        (1,1) : ((0.5*(1-mutate_prob))**2) + ((0.5*mutate_prob)**2) + (2*(0.5*(mutate_prob)*0.5*(1-mutate_prob))), # 0.25
        # Dad 1 gene, Mum 2 genes
        (1,2) : ((0.5*(1-mutate_prob)) * mutate_prob) + (0.5*(mutate_prob)*mutate_prob), # 0.005
        # Dad 2 genes, Mum 0 genes
        (2,0) : (1-mutate_prob) * mutate_prob, # 0.0099
        # Dad 2 genes, Mum 1 gene
        (2,1) : ((0.5*(1-mutate_prob)) * mutate_prob) + (0.5*(mutate_prob)*mutate_prob), # 0.005
        # Dad 2 genes, Mum 2 genes
        (2,2) : mutate_prob ** 2 # 0.0001
    },

    # If child has 1 gene
    1 : {
        # Dad 0 gene, Mum 0 gene
        (0,0) : 2*(mutate_prob*(1-mutate_prob)), # 0.0198
        # Dad 0 gene, Mum 1 gene
        (0,1) : ((1-mutate_prob)*(0.5*mutate_prob + 0.5*(1-mutate_prob))) + (mutate_prob*(0.5*mutate_prob + 0.5*(1-mutate_prob))), # 0.5
        # Dad 0 gene, Mum 2 genes
        (0,2) : ((1-mutate_prob)**2) + ((mutate_prob)**2), # 0.9802
        # Dad 1 gene, Mum 0 gene
        (1,0) : ((1-mutate_prob)*(0.5*mutate_prob + 0.5*(1-mutate_prob))) + (mutate_prob*(0.5*mutate_prob + 0.5*(1-mutate_prob))), # 0.5
        # Dad 1 gene, Mum 1 gene
        (1,1) : 4*(0.5*(1-mutate_prob)*0.5*(mutate_prob)) + 2*((0.5*(1-mutate_prob))**2) + 2*(0.5*0.5*mutate_prob*mutate_prob), # 0.5
        # Dad 1 gene, Mum 2 genes
        (1,2) : ((0.5*(1-mutate_prob)*(1-mutate_prob)) + (0.5*mutate_prob*mutate_prob)) + (2*(0.5*(1-mutate_prob)*mutate_prob)), # 0.5
        # Dad 2 genes, Mum 0 genes
        (2,0) : ((1-mutate_prob)**2) + ((mutate_prob)**2), # 0.9802
        # Dad 2 genes, Mum 1 gene
        (2,1) : ((0.5*(1-mutate_prob)*(1-mutate_prob)) + (0.5*mutate_prob*mutate_prob)) + (2*(0.5*(1-mutate_prob)*mutate_prob)),# 0.5
        # Dad 2 genes, Mum 2 genes
        (2,2) : 2*(mutate_prob*(1-mutate_prob)) # 0.0198
    },

    # If child has 2 gene
    2 : {
        # Dad 0 gene, Mum 0 gene
        (0,0) : mutate_prob ** 2, # 0.0001
        # Dad 0 gene, Mum 1 gene
        (0,1) : mutate_prob * (0.5*(1-mutate_prob) + 0.5*(mutate_prob)), # 0.005
        # Dad 0 gene, Mum 2 genes
        (0,2) : mutate_prob * (1-mutate_prob), # 0.0099
        # Dad 1 gene, Mum 0 gene
        (1,0) : mutate_prob * (0.5*(1-mutate_prob) + 0.5*(mutate_prob)), # 0.005
        # Dad 1 gene, Mum 1 gene
        (1,1) : ((0.5*(1-mutate_prob))**2) + ((0.5*mutate_prob)**2) + 2*(0.5*0.5*mutate_prob*(1-mutate_prob)), # 0.25
        # Dad 1 gene, Mum 2 genes
        (1,2) : (0.5*mutate_prob + 0.5*(1-mutate_prob)) * (1-mutate_prob), # 0.495
        # Dad 2 genes, Mum 0 genes
        (2,0) : mutate_prob * (1-mutate_prob), # 0.0099
        # Dad 2 genes, Mum 1 gene
        (2,1) : ((0.5*mutate_prob + 0.5*(1-mutate_prob)) * (1-mutate_prob)), # 0.495
        # Dad 2 genes, Mum 2 genes
        (2,2) : ((1-mutate_prob)**2) # 0.9801
    }
}

def prepro_joint(num_gene, dad_num_gene, mum_num_gene):
    parents_num_genes = (dad_num_gene, mum_num_gene)
    prob = COND_PROB_TABLE[num_gene][parents_num_genes]
    return prob

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    joint = 1 # Initialization
    for person in people:
    # Person number of genes
        if person in one_gene:
            num_gene = 1
        elif person in two_genes:
            num_gene = 2
        else:
            num_gene = 0
        
        #traits
        person_has_trait = person in have_trait
        joint *= PROBS['trait'][num_gene][person_has_trait]

        if people[person]['father'] is None: # If person does not have parents, use unconditional probabilities
            # gene
            joint *= PROBS['gene'][num_gene]

        else: # If person has parents, use conditional probabilities
            # gene
            father = people[person]['father']
            mother = people[person]['mother']

            if father in one_gene:
                dad_num_gene = 1
            elif father in two_genes:
                dad_num_gene = 2
            else:
                dad_num_gene = 0
            
            if mother in one_gene:
                mum_num_gene = 1
            elif mother in two_genes:
                mum_num_gene = 2
            else:
                mum_num_gene = 0

            joint *= prepro_joint(num_gene,dad_num_gene,mum_num_gene)

    return joint 

            
            


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities.keys():
        if person in one_gene:
            probabilities[person]['gene'][1] += p
            if person in have_trait:
                probabilities[person]['trait'][True] += p
            else:
                probabilities[person]['trait'][False] += p

        elif person in two_genes:
            probabilities[person]['gene'][2] += p
            if person in have_trait:
                probabilities[person]['trait'][True] += p
            else:
                probabilities[person]['trait'][False] += p

        else:
            probabilities[person]['gene'][0] += p
            if person in have_trait:
                probabilities[person]['trait'][True] += p
            else:
                probabilities[person]['trait'][False] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities.keys():
        # gene
        gene_prob_0 = probabilities[person]['gene'][0]
        gene_prob_1 = probabilities[person]['gene'][1]
        gene_prob_2 = probabilities[person]['gene'][2]
        gene_prob_sum = gene_prob_0 + gene_prob_1 + gene_prob_2
        gene_alpha = 1/gene_prob_sum
        for i in range(0,3):
             probabilities[person]['gene'][i] *= gene_alpha
        
        # trait
        trait_prob_true = probabilities[person]['trait'][True]
        trait_prob_false = probabilities[person]['trait'][False]
        trait_prob_sum = trait_prob_true + trait_prob_false
        trait_alpha = 1/trait_prob_sum
        probabilities[person]['trait'][True] *= trait_alpha
        probabilities[person]['trait'][False] *= trait_alpha

if __name__ == "__main__":
    main()
