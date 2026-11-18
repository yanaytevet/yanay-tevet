import {JapaneseStrings} from './en';

export const ja: JapaneseStrings = {
  title: '日本語',
  subtitle: '文章、例文、単語、漢字、助詞、文法がつながったネットワークを探索しましょう。',
  nav: {
    explore: '探索',
    ingest: '取り込み',
    review: 'レビュー',
  },
  tabs: {
    passage: '文章',
    sentence: '例文',
    word: '単語',
    kanji: '漢字',
    particle: '助詞',
    rule: '文法',
  },
  nodeTypes: {
    passage: '文章',
    sentence: '例文',
    word: '単語',
    kanji: '漢字',
    particle: '助詞',
    rule: '文法',
  },
  statuses: {
    stub: '未作成',
    generating: '生成中',
    needs_review: 'レビュー待ち',
    published: '公開済み',
  },

  explore: {
    shuffle: 'シャッフル',
    loadFailed: '読み込めませんでした。少し待ってからもう一度お試しください。',
    emptyText: '取り込んだテキストと、そこから生成された項目がここに表示されます。',
    emptyTitles: {
      passage: '文章はまだありません',
      sentence: '例文はまだありません',
      word: '単語はまだありません',
      kanji: '漢字はまだありません',
      particle: '助詞はまだありません',
      rule: '文法はまだありません',
    },
  },

  speak: {
    readAloud: '日本語で読み上げ',
    stop: '停止',
    loop: 'リピート',
    loopOn: 'リピート中',
  },

  detail: {
    loading: '読み込み中',
    notFound: 'ノードが見つかりません。',
    backToJapanese: '日本語トップに戻る',
    radicals: '部首：{radicals}',
    noContent: 'まだ内容がありません。',
    noContentAdmin: 'まだ内容がありません。「内容を生成」をクリックして作成してください。',
    linksFrom: 'このノードからのリンク',
    linksTo: 'このノードへのリンク',
    outgoing: {
      contains: '含む',
      composed_of: '構成要素',
      uses_rule: '使われている文法',
      example_of: '用例の対象',
      exception_to: '例外の対象',
      synonym_of: '類義語',
      related_to: '関連',
      same_kanji_as: '同じ漢字',
    },
    incoming: {
      contains: '出てくる箇所',
      composed_of: 'この字を使う単語',
      uses_rule: 'この文法を使う例文',
      example_of: '用例',
      exception_to: '例外',
      synonym_of: '類義語',
      related_to: '関連',
      same_kanji_as: '同じ漢字',
    },

    editTitle: 'タイトルを編集',
    generateContent: '内容を生成',
    approve: '承認',
    regenerate: '再生成',
    generateDialog: {
      text: 'モデルへの指示（任意）。例：「漢字表記の 中 を使う」「動詞ではなく名詞として扱う」「丁寧なコピュラ」。空欄のままにすると標準のルールで生成します。',
      label: 'メモ（任意）',
      confirm: '生成',
    },
    editTitleDialog: {
      text: 'このノードに表示するメインのテキストを更新します。単語や例文には 漢字(かんじ) のようにふりがなを付けられます。',
      label: 'タイトル',
      confirm: '保存',
    },
    error: 'エラー',
    generateFailed: '内容を生成できませんでした：{error}',
    updateTitleFailed: 'タイトルを更新できませんでした：{error}',
    approveFailed: '承認できませんでした：{error}',
  },
};
