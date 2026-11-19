from src.stats.cooccurrence import extract_top_neighbors
from src.stats.corpus import load_sentences
from src.stats.information_theory import (
    build_huffman_codes,
    compute_letter_frequencies,
    evaluate_encoding,
)
from src.stats.zipf import (
    compute_word_frequencies,
    extract_core_vocabulary,
    fit_zipf_power_law,
    plot_zipf_distribution,
)

CORPUS_PATH = "data/latvian_corpus.txt"
PLOT_PATH = "results/zipf_distribution.png"
CORE_VOCAB_PATH = "results/core_vocabulary_90.csv"
NEIGHBORS_PATH = "results/top_100_neighbors.csv"


def run_stats() -> None:
    sentences = load_sentences(CORPUS_PATH)
    words = [word for sentence in sentences for word in sentence]

    # 1. Letter frequencies & Huffman
    freqs = compute_letter_frequencies(words)
    codes = build_huffman_codes(freqs)
    metrics = evaluate_encoding(freqs, codes)

    total_letters = sum(count for _, count, _ in freqs)
    print(f"Total words: {len(words):,} | Total letters: {total_letters:,}\n")

    print(f"{'Rank':<6}{'Letter':<8}{'Count':<12}{'Percentage':<14}{'Huffman Code':<14}{'Bits'}")
    print("-" * 60)
    for rank, (letter, count, pct) in enumerate(freqs, start=1):
        code = codes[letter]
        print(f"{rank:<6}{letter:<8}{count:<12,}{f'{pct:.4f}%':<14}{code:<14}{len(code)}")

    print("-" * 60)
    print(f"Shannon Entropy             : {metrics['shannon_entropy']:.4f} bits/letter")
    print(f"Huffman Average Code Length : {metrics['avg_code_length']:.4f} bits/letter")
    print(f"Encoding Efficiency         : {metrics['efficiency_pct']:.2f}%\n")

    # 2. Zipf's Law Analysis
    word_freqs = compute_word_frequencies(words)
    zipf_metrics = fit_zipf_power_law(word_freqs)
    plot_zipf_distribution(word_freqs, zipf_metrics, output_path=PLOT_PATH)

    print(f"Unique words (Vocabulary Size) : {len(word_freqs):,}")
    print(f"Fitted Zipf Exponent (s)       : {zipf_metrics['exponent_s']:.4f}")
    print(f"Log-Log Goodness of Fit (R^2)  : {zipf_metrics['r_squared']:.4f}\n")

    print(f"{'Rank':<8}{'Word':<16}{'Count':<10}{'Percentage':<14}{'r * f'}")
    print("-" * 60)
    for rank, word, count, pct in word_freqs[:20]:
        print(f"{rank:<8}{word:<16}{count:<10,}{f'{pct:.4f}%':<14}{rank * count:,}")

    print("-" * 60)
    print(f"Saved Zipf log-log plot to: {PLOT_PATH}")

    # 3. 90% Core Vocabulary
    core_metrics = extract_core_vocabulary(
        word_freqs, target_coverage_pct=90.0, output_path=CORE_VOCAB_PATH
    )
    print(
        f"90% Corpus Coverage            : {core_metrics['core_word_count']:,} / {len(word_freqs):,} words "
        f"({core_metrics['vocab_share_pct']:.2f}% of vocabulary)"
    )
    print(f"Exact Cumulative Coverage      : {core_metrics['actual_coverage_pct']:.4f}%")
    print(f"Saved 90% core vocabulary to   : {CORE_VOCAB_PATH}")

    # 4. Word Co-occurrence / Neighbors
    top_neighbors = extract_top_neighbors(sentences, top_n=100, output_path=NEIGHBORS_PATH)

    print("-" * 60)
    print(f"Saved top 100 words by unique neighbors : {NEIGHBORS_PATH}\n")
    print(f"{'Rank':<8}{'Word':<18}{'Unique Neighbors'}")
    print("-" * 60)
    for rank, word, count in top_neighbors[:20]:
        print(f"{rank:<8}{word:<18}{count:,}")