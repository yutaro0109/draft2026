# 2026 ドラフト速報 — 無料GitHub Pages版

## できること
- 横12球団（NPB公表の2026年ウェーバー順）、縦1〜12位、支配下・育成を切替
- 72人ランキングを表示し、確定指名を候補リストから自動除外
- GitHub Actionsが速報元のHTMLを取得し、`data.json`を更新
- iPhone Safariで閲覧可能（GitHub Pages公開後）

## 初期設定
1. GitHubで**公開リポジトリ**を新規作成する。
2. このZIPの中身（隠しフォルダ `.github` も含む）をリポジトリのルートへアップロードする。
3. Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` → Save。
4. Settings → Actions → General → Workflow permissions で Read and write permissions を許可（組織設定により不可の場合あり）。
5. Actions → Draft data update → Run workflow を押して初回取得を実行。
6. `https://<GitHubユーザー名>.github.io/<リポジトリ名>/` をiPhone Safariで開く。
7. Safariの共有 → ホーム画面に追加。

## 重要な制約
- **未検証**：速報元サイトの実際のHTML構造が取得環境で確認できなかったため、`fetch.py` の解析は汎用的な試作です。自動取得が正常に機能する保証はありません。
- `data.json` の `status: error` は取得・解析失敗です。架空の指名データは生成しません。
- GitHub Actionsのscheduleは最短5分、実行遅延あり。画面側20秒更新でも**リアルタイムにはなりません**。
- 速報サイトの利用条件・自動アクセス許可・転載条件は公開前に確認してください。許可がない場合はこの取得処理を使わないでください。
- 1位は「入札候補」ではなく交渉権確定後の選手だけを表示する想定。
- 氏名の表記揺れは一部正規化。完全な名寄せには手動確認が必要です。
- GitHub Actionsの定期実行は公開リポジトリで無料枠を利用しやすいですが、サービスの利用条件は変わり得ます。

## データ仕様
`data.json`: `{"updated_at":"...", "status":"ok", "picks":[{"team":"楽天","round":1,"kind":"支配下","name":"渡部海","school":"青山学院大"}]}`
候補者は `candidates.json` で編集できます。
