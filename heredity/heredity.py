import csv
import itertools
import sys

PROBS = {

    # Probabilidades incondicionais de ter gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probabilidade de característica dada duas cópias do gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probabilidade de característica dada uma cópia do gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probabilidade de característica dada nenhuma cópia do gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}

#Carregar os dados do arquivo.
#Testar todas as combinações possíveis de quem pode ter 0, 1 ou 2 cópias do gene e quem pode ter o traço.
#Calcular a probabilidade conjunta para cada configuração.
#Atualizar as probabilidades de cada pessoa.
#Normalizar as probabilidades para garantir que somam 1.
#Exibir os resultados.


def main():

    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Acompanhe as probabilidades genéticas e características de cada pessoa
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

    # Passe por todos os grupos de pessoas que possam ter a característica
    names = set(people)
    for have_trait in powerset(names):

        # Verifique se o conjunto atual de pessoas viola informações conhecidas
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Faça um loop sobre todos os grupos de pessoas que possam ter o gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Atualizar probabilidades com nova probabilidade conjunta
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Certifique-se de que as probabilidades somam 1
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
    Carregue dados de genes e características de um arquivo em um dicionário.
    Arquivo assumido como um CSV contendo os campos nome, mãe, pai, característica.
    mãe, pai devem estar em branco ou ambos devem ser nomes válidos no CSV.
    trait deve ser 0 ou 1 se trait for conhecido; caso contrário, em branco.
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
    Retorne uma lista de todos os subconjuntos possíveis do conjunto s.
    gera combinações das pessoas que possuem a caracteristica com as que possuem um ou dois genes
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def parents_prob(parent, two_genes, one_gene):
    if parent in two_genes:
        return 1 - PROBS["mutation"]
    elif parent in one_gene:
        return 0.5
    else:
        return PROBS["mutation"]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Calcule e retorne uma probabilidade conjunta.

    A probabilidade retornada deve ser a probabilidade de que
        * todos no conjunto `one_gene` possuem uma cópia do gene, e
        * todos no conjunto `two_genes` possuem duas cópias do gene, e
        * todos que não estão em `one_gene` ou `two_gene` não possuem o gene, e
        * todos no conjunto `have_trait` possuem a característica, e
        * todos que não estão no set` have_trait` não possuem a característica.


    """
    probability = 1
    
    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]

        if person in two_genes:
            num_genes = 2
        elif person in one_gene:
            num_genes = 1
        else:
            num_genes = 0
        
        if mother is None and father is None:
            gene_prob = PROBS["gene"][num_genes]
        else:
            mother_prob = parents_prob(mother, two_genes, one_gene)
            father_prob = parents_prob(father, two_genes, one_gene)

            if num_genes == 2:
                gene_prob = mother_prob * father_prob
            elif num_genes == 1:
                gene_prob = (mother_prob * (1 - father_prob)) + ((1 - mother_prob) * father_prob)
            else:
                gene_prob = (1 - father_prob) * (1 - mother_prob)
        
        trait_prob = PROBS["trait"][num_genes][person in have_trait]
        
        probability *= gene_prob * trait_prob  
    return probability  


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Adicione às `probabilidades` uma nova probabilidade conjunta `p`.
    Cada pessoa deve ter suas distribuições de “genes” e “características” atualizadas.
    Qual valor para cada distribuição é atualizado depende se
    a pessoa está em `have_gene` e `have_trait`, respectivamente.
    """
    for person in probabilities:
        if person in two_genes:
            num_genes = 2
        elif person in one_gene:
            num_genes = 1
        else:
            num_genes = 0
        
        has_trait = person in have_trait

        probabilities[person]["gene"][num_genes] += p
        probabilities[person]["trait"][has_trait] += p



def normalize(probabilities):
    """
    Atualize as `probabilidades` de modo que cada distribuição de probabilidade
    é normalizado (ou seja, soma 1, com proporções relativas iguais).
    """
    for person in probabilities:
        gene_total= sum(probabilities[person]["gene"].values())
        if gene_total > 0:
            for gene in probabilities[person]["gene"]:
                probabilities[person]["gene"][gene] /= gene_total

        trait_total =  sum(probabilities[person]["trait"].values())
        if trait_total > 0:
            for trait in probabilities[person]["trait"]:
                probabilities[person]["trait"][trait] /= trait_total

if __name__ == "__main__":
    main()