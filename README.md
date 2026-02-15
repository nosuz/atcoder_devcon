# Dev Container for AtCoder

このDev Containerは、[AtCoder Beginner Contest (ABC)](https://atcoder.jp/home)に参加するコード作成環境です。

- テンプレートからスケルトンコードを自動生成します。
- Webページから各問題の入力例・出力例を取得してテストコードを自動作成します。
- Chromeの拡張機能`atcoder-paster`を使用すると、Javaのソースコードから`package`宣言を削除して、クラス名を`Main`に置換してコードを提出欄に貼り付けます。

## Dev Container

コンテナを作成する手順は、次のとおりです。

1. このレポジトリをクローンする。
2. UID と GID を確認する。

もしローカルの UID と GID が次の表と異なる場合は、次のいずれかのコマンドを実行してローカルの ID がコンテナに反映されるように設定してください。この操作がないと、docker image の作成に時間がかかり、作成された image のサイズも大きくなります。

|     | ID   |
| --- | ---- |
| UID | 1000 |
| GID | 1000 |

1. VSCode で開き、コマンドパレットから`Dev Containers: Rebuild Container`を実行する。

```bash
bash .devcontainer/generate_env.sh
# or
python .devcontainer/generate_env.py
```

以上で、プログラミング環境の他、問題の入出力例を取得するプログラムが使えるようになります。

## Supporting Languages

- Python
- Java

Javaのコードを提出する時には、スケルトンコードのままだとエラーになります。そのため次の修正が必要です。

- package宣言を削除する。
- クラス名をMainに修正する。

この不便さは、次のChrome拡張機能または[bookmarklet](bookmarklet.js)を使用すると解消されます。

### Chrome拡張機能

ブックマークレットの代わりにChrome拡張機能を使用することもできます。

#### 拡張機能のインストール方法

1. 拡張機能から、拡張機能の管理を開く。
2. ディベロッパーモードを有効にする。
3. 「パケージ化されていない拡張機能を読み込む」をクリックして、`atcode-paster`ディレクトリを選択する。
4. 「すべての拡張機能」に表示されるので、拡張機能を有効にする。

#### 拡張機能の使用方法

1. AtCoderの各問題または提出ページに移動する。
2. 拡張機能のリストから`atcoder-paster`を選択する。ピン止めしておくと便利。
3. 「.javaを選んで貼り付け」ボタンが表示されるので、クリックする。
4. 貼り付けるファイルを選択する。

### Bookmarklet

```javascript
javascript:(async()=>{try{const[p]=await showOpenFilePicker({types:[{accept:{"text/plain":[".java"]}}],excludeAcceptAllOption:true});let c=await(await p.getFile()).text();c=c.replace(/^\s*package\s+.*;\s*$/m,"");if(!/public\s+class\s+Main\b/.test(c))c=c.replace(/public\s+class\s+[A-Za-z_]\w*\s*\{/m,"public class Main {");let ok=false;if(window.monaco?.editor?.getModels){let m=window.monaco.editor.getModels();if(m[0]){m[0].setValue(c);ok=true}}if(!ok&&window.ace?.edit){let e=document.querySelector(".ace_editor")||document.getElementById("editor");if(e){let ed=ace.edit(e);ed.setValue(c,-1);ed.clearSelection();ok=true}}let ta=document.querySelector('textarea[name="sourceCode"]');if(ta){ta.value=c;ta.dispatchEvent(new Event("input",{bubbles:true}));ta.dispatchEvent(new Event("change",{bubbles:true}));ok=true}if(!ok)return;window.scrollTo(0,document.documentElement.scrollHeight)}catch(e){}})();
```

#### Bookmarkletの使用方法

1. 問題のページまたは提出ページを開く。
2. 提出するコードの言語を選択する。
3. このbookmarkletを実行する。
4. ファイル選択画面が表示されるので、提出するコードを選択する。
5. 提出ボタンをクリックする。

## Setup

### ログイン

コンテストに参加するためには、AtCoderのページにログインする必要があります。しかしロボット判定があるため、一般的なブラウザ以外ではログインできません。そこで、ログイン済みのブラウザーから必要な情報をコピーします。

Chrome Browserでの例

1. [Atcoder](https://atcoder.jp/)のページを開いて、ログインする。
2. `F12`で開発者ツールを開く。
3. 開発者ツールのメニューバーにあるApplicationを選ぶ。
4. StorageのCookiesを選ぶ。
5. `https://atcoder.jp`があるので、これをクリックする。
6. `REVEL_SESSION`の値をコピーする。
7. `cookies_sample.json`を開いて、REVEL_SESSIONの値をコピーした値で置き換える。
8. `cookies_sample.json`を`cookies.json`として保存する。

コンテスト時に入力・出力例を取得できなくなったときには、再度この操作が必要です。

#### ログインテスト

ログイン状態かは、次のコマンドで確認できます。

```bash
./setup.py --login
```

`Screen Name`が表示されない場合は、ログイン状態が解除されています。Web Browserからcookie情報をコピーしてください。

### 入力・出力例の取得とコード作成

スケルトンコードとテストコードの作成には、`setup.py`を使用します。例えばABC439のコードを作成するには、次のコマンドを実行します。

```bash
./setup.py abc439
```

このコマンドを実行すると、`default_lang.txt`で指定した言語用のスケルトンコードとテストコードが作成されます。オプションにより、作成する言語を指定することができます。

### Options

- --python, --java: それぞれPythonとJava用のスケルトンコードとテストコードを作成します。

### default_lang.txt

`default_lang.txt`は、`setup.py`がオプションの指定なしに実行された時に作成する言語を指定します。

- #から始まる行は、コメントとなる。
- 言語は、各1行で指定する。

## Testing Codes

### Python

Pythonのテスト環境は、[pytest](https://docs.pytest.org/en/stable/)を使う方法と、`validate.py`を使う方法があります。

#### pytest

`pytest`を使った入力・出力例でのテスト

```bash
# A問題のテスト
pytest tests/test_a.py

# 個別の入力例でテスト
pytest tests/test_a.py -k sample1
pytest tests/test_a.py -k sample2

```

#### validate.py

`validate.py`を使った入力・出力例でのテスト

`validate.py`用の入力・出力例は、コードにコメントとして記載します。そのため自作の入力例を簡単にテストすることができます。

```bash
# A問題のテスト
python ../validate.py A.py

# 個別の入力例でテスト
python ../validate.py A.py --limit 1
python ../validate.py A.py --limit 1,2

```

### Java

`JUnit`を使った入力・出力例でのテスト

```bash
# A問題のテスト
gradle test --tests ATest

# 個別の入力例でテスト
gradle test --tests ATest.sample1
gradle test --tests ATest.sample2

```

## Troubleshooting

### ファイルを書き込めない

Dev Containerを実行しているユーザIDとファイルオーナーのIDが一致していないと考えられます。

IDを一致させるため、一度Dev Containerを終了させてください。その上で次のコマンドを実行して、再度Dev Containerを再作成してください。

```bash
bash .devcontainer/generate_env.sh
# or
python .devcontainer/generate_env.py
```

### Git の編集にVSCodeを使用したい

editor が設定されていないため、コマンドラインから`git commit --amend`など編集が必要な操作ができません。そこで、`.git/config`に`editor`の設定を加えます。

```
[core]
 editor = code --wait
```

ローカルの`~/.gitconfig`に設定がある場合は、デフォルト設定ではこのファイルがコピーされるのでコンテナ毎の設定は不要です。
