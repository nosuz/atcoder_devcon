# Markdown の書き方

## 数式

LaTeXの表記方法を使うことで、Markdown中に数式を書くことができます。

主な数学記号は次のとおりです。

|            | LaTeX表記         |
| ---------- | ----------------- |
| 下付き文字 | A_i A_{i+1}       |
| 上付き文字 | A^a A^{i+1}       |
| 積和       | \sum_{i=0}^{N}    |
| 分数       | \frac{分子}{分母} |
| ルート     | \sqrt{2}          |
| 点々       | \cdots            |
|            |                   |

### インライン

本文中に数式を書く場合は、`$`と`$`で数式を囲む。なお、この前後に空白が必要です。数式にMarkdownの構文と重複がある場合は、`$`と`$`の内側をバックスラッシュで囲む。

```
数式 $\sum_{i=0}^n P_i$ をインラインに入れる例。
数式 $`\sum_{i=0}^n P_i`$ をインラインに入れる例。
```

## ブロック

数式のブロックは`$$`行で挟む。複数の式を改行して書きたい場合は、`aligned`環境で`\\`を行末に置く。

`\tag{番号}`を付けると、数式が崩れる。

```
$$
\sum_{i=0}^n P \ge \sum_{i=0}^N W - \sum_{i=0}^n W
$$

$$
\begin{aligned}
\sum_{i=0}^n P \ge \sum_{i=0}^N W - \sum_{i=0}^n W \\
\sum_{i=0}^n P + \sum_{i=0}^n W \ge \sum_{i=0}^N W
\end{aligned}
$$
```

$$
\sum_{i=0}^n P \ge \sum_{i=0}^N W - \sum_{i=0}^n W
$$

$$
\begin{aligned}
\sum_{i=0}^n P \ge \sum_{i=0}^N W - \sum_{i=0}^n W \\
\sum_{i=0}^n P + \sum_{i=0}^n W \ge \sum_{i=0}^N W
\end{aligned}
$$
