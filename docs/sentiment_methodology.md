# Sentiment analysis methodology

How `src/sentiment.py`, `src/train_sentiment.py` and
`src/run_feedback_analysis.py` turn raw customer feedback into a sentiment
score and a rating label.

## Problem

For each of the 97 customer reviews we want:

1. a **sentiment score** between 0 and 1, and
2. a **rating label**: `Excellent`, `Good` or `Needs Improvement`.

## Approach: knowledge distillation

The raw feedback has no human labels, so a supervised model cannot be trained
directly. Instead we use **weak supervision / distillation**:

1. **Teacher.** A pretrained transformer
   (`cardiffnlp/twitter-roberta-base-sentiment-latest`) labels every review. It
   returns three class probabilities; we convert them to a 0-1 score with

   ```
   score = P(positive) + 0.5 * P(neutral)
   ```

   so that neutral text lands in the middle of the range. This teacher is the
   most accurate scorer and needs `torch` + `transformers`.

2. **Student.** Several lightweight scikit-learn pipelines are compared with
   stratified 5-fold cross-validation and the best one is refit on all data:

   | Vectorizer | Classifiers |
   | --- | --- |
   | word TF-IDF (1-2 grams) | LogisticRegression, LinearSVC, ComplementNB |
   | char TF-IDF (3-5 grams) | LogisticRegression, LinearSVC, ComplementNB |

   The winner is wrapped in a sigmoid calibrator so it exposes
   `predict_proba`, then saved to `models/sentiment_model.joblib`. It runs
   without `torch`, which keeps the default pipeline fast.

## Results (97 reviews)

| Vectorizer | Classifier | Accuracy | Macro F1 |
| --- | --- | --- | --- |
| **char** | **LinearSVC** | **0.897** | **0.865** |
| char | LogisticRegression | 0.897 | 0.865 |
| word | ComplementNB | 0.876 | 0.845 |
| char | ComplementNB | 0.876 | 0.835 |
| word | LinearSVC | 0.866 | 0.824 |
| word | LogisticRegression | 0.835 | 0.797 |

Metrics are stored in [`models/sentiment_metrics.json`](../models/sentiment_metrics.json).

## Score to label

The thresholds match the Power BI dashboard bands:

| Score | Label |
| --- | --- |
| `>= 0.80` | Excellent |
| `> 0.50` and `< 0.80` | Good |
| `<= 0.50` | Needs Improvement |

The score produced by the student is the **expected value** of the calibrated
class probabilities (`Excellent = 1`, `Good = 0.5`, `Needs Improvement = 0`).

## Three interchangeable scorers

`src/sentiment.py` exposes a common `score(texts) -> Series` interface:

| Scorer | Backend | Needs torch | Role |
| --- | --- | --- | --- |
| `TransformerSentimentScorer` | RoBERTa | yes | Most accurate (teacher) |
| `SklearnSentimentScorer` | TF-IDF + LinearSVC | no | Default, distilled |
| `LexiconSentimentScorer` | VADER | no | Fallback baseline |

`get_default_scorer()` picks the first available in the order
`sklearn -> transformer -> vader`.

## Word clouds

`src/word_analysis.py` counts words (stop words removed) and renders dark-theme
word clouds for all feedback, positive feedback and negative feedback, plus a
top-20 bar chart. Colours are assigned deterministically so the images are
reproducible.

## Reproducing

```bash
# Retrain the student from the transformer teacher (needs requirements-ml.txt)
pip install -r requirements-ml.txt
python -m src.train_sentiment

# Run the analysis (uses the saved sklearn model)
python -m src.run_feedback_analysis
```

## Limitations

- The teacher labels are model-generated, not human-annotated, so the reported
  accuracy measures agreement with the teacher rather than ground truth.
- The dataset is small (97 reviews), so cross-validation metrics have wide
  error bars.
- English-only; the transformer and VADER lexicons are English.
