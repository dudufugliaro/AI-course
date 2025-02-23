import os
import random
import re
import sys

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
    Analise um diretório de páginas HTML e verifique links para outras páginas.
    Retorne um dicionário onde cada chave é uma página e os valores são
    uma lista de todas as outras páginas do corpus vinculadas pela página.
    """
    pages = dict()

    # Extraia todos os links de arquivos HTML
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Incluir apenas links para outras páginas no corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Retorna um dicionário representando a distribuição de probabilidade
    de qual página um surfista aleatório visitaria a seguir.
    """
    probabilities = {}
    links = corpus.get(page, set())
    num_pages = len(corpus)
    
    if links:
        for p in corpus:
            probabilities[p] = (1 - damping_factor) / num_pages
        for link in links:
            probabilities[link] += damping_factor / len(links)
    else:
        for p in corpus:
            probabilities[p] = 1 / num_pages
    
    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Retorna os valores ESTIMADOS de PageRank para cada página por meio de amostragem.
    """
    pagerank = {page: 0 for page in corpus}
    page = random.choice(list(corpus.keys()))
    
    for _ in range(n):
        pagerank[page] += 1
        model = transition_model(corpus, page, damping_factor)
        page = random.choices(list(model.keys()), weights=model.values())[0]
    
    for page in pagerank:
        pagerank[page] /= n
    
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Retorna os valores de PageRank calculados iterativamente ATE A CONVERGENCIA.
    """
    num_pages = len(corpus)
    pagerank = {page: 1 / num_pages for page in corpus}
    threshold = 0.001
    
    while True:
        new_pagerank = {}
        for page in corpus:
            rank = (1 - damping_factor) / num_pages
            for possible_link in corpus:
                if page in corpus[possible_link]:
                    rank += damping_factor * (pagerank[possible_link] / len(corpus[possible_link]))
                if not corpus[possible_link]:  # Página sem links
                    rank += damping_factor * (pagerank[possible_link] / num_pages)
            new_pagerank[page] = rank
        
        if all(abs(new_pagerank[p] - pagerank[p]) < threshold for p in pagerank):
            break
        
        pagerank = new_pagerank
    
    return pagerank


if __name__ == "__main__":
    main()
