import {JapaneseStrings} from './en';

export const zhHans: JapaneseStrings = {
  title: '日语',
  subtitle: '探索由文章、句子、单词、汉字、助词和语法规则组成的网络。',
  nav: {
    explore: '探索',
    ingest: '导入',
    review: '审核',
  },
  tabs: {
    passage: '文章',
    sentence: '句子',
    word: '单词',
    kanji: '汉字',
    particle: '助词',
    rule: '语法',
  },
  nodeTypes: {
    passage: '文章',
    sentence: '句子',
    word: '单词',
    kanji: '汉字',
    particle: '助词',
    rule: '语法',
  },
  statuses: {
    stub: '待生成',
    generating: '生成中',
    needs_review: '待审核',
    published: '已发布',
  },

  explore: {
    shuffle: '随机换一批',
    loadFailed: '加载失败，请稍后重试。',
    emptyText: '导入的文本以及由此生成的条目会显示在这里。',
    emptyTitles: {
      passage: '还没有文章',
      sentence: '还没有句子',
      word: '还没有单词',
      kanji: '还没有汉字',
      particle: '还没有助词',
      rule: '还没有语法',
    },
  },

  speak: {
    readAloud: '用日语朗读',
    stop: '停止',
    loop: '循环',
    loopOn: '循环播放中',
  },

  detail: {
    loading: '加载中',
    notFound: '找不到该节点。',
    backToJapanese: '返回日语',
    radicals: '部首：{radicals}',
    noContent: '还没有内容。',
    noContentAdmin: '还没有内容。点击“生成内容”来创建。',
    linksFrom: '从此节点出发的链接',
    linksTo: '指向此节点的链接',
    outgoing: {
      contains: '包含',
      composed_of: '组成部分',
      uses_rule: '使用的语法',
      example_of: '是以下内容的例子',
      exception_to: '是以下内容的例外',
      synonym_of: '同义词',
      related_to: '相关',
      same_kanji_as: '相同汉字',
    },
    incoming: {
      contains: '出现于',
      composed_of: '用于单词',
      uses_rule: '使用此语法的句子',
      example_of: '例子',
      exception_to: '例外',
      synonym_of: '同义词',
      related_to: '相关',
      same_kanji_as: '相同汉字',
    },

    editTitle: '编辑标题',
    generateContent: '生成内容',
    approve: '批准',
    regenerate: '重新生成',
    generateDialog: {
      text: '用于引导模型的备注（可选），例如“使用汉字写法 中”“当作名词而不是动词”“这是礼貌的系词”。留空则按默认规则生成。',
      label: '备注（可选）',
      confirm: '生成',
    },
    editTitleDialog: {
      text: '更新此节点显示的主要文本。单词和句子可以加上振假名，例如 漢字(かんじ)。',
      label: '标题',
      confirm: '保存',
    },
    error: '错误',
    generateFailed: '无法生成内容：{error}',
    updateTitleFailed: '无法更新标题：{error}',
    approveFailed: '无法批准：{error}',
  },
};
