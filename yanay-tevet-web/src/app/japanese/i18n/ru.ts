import {JapaneseStrings} from './en';

export const ru: JapaneseStrings = {
  title: 'Японский',
  subtitle: 'Исследуйте сеть текстов, предложений, слов, кандзи, частиц и грамматических правил.',
  nav: {
    explore: 'Обзор',
    ingest: 'Импорт',
    review: 'Проверка',
  },
  tabs: {
    passage: 'Тексты',
    sentence: 'Предложения',
    word: 'Слова',
    kanji: 'Кандзи',
    particle: 'Частицы',
    rule: 'Правила',
  },
  nodeTypes: {
    passage: 'Текст',
    sentence: 'Предложение',
    word: 'Слово',
    kanji: 'Кандзи',
    particle: 'Частица',
    rule: 'Правило',
  },
  statuses: {
    stub: 'Заготовка',
    generating: 'Создаётся',
    needs_review: 'Нужна проверка',
    published: 'Опубликовано',
  },

  explore: {
    shuffle: 'Перемешать',
    loadFailed: 'Не удалось загрузить. Попробуйте чуть позже.',
    emptyText: 'Здесь появятся импортированные тексты и созданные из них элементы.',
    emptyTitles: {
      passage: 'Текстов пока нет',
      sentence: 'Предложений пока нет',
      word: 'Слов пока нет',
      kanji: 'Кандзи пока нет',
      particle: 'Частиц пока нет',
      rule: 'Правил пока нет',
    },
  },

  speak: {
    readAloud: 'Прочитать вслух по-японски',
    stop: 'Стоп',
    loop: 'Повтор',
    loopOn: 'Повтор включён',
  },

  detail: {
    loading: 'Загрузка',
    notFound: 'Узел не найден.',
    backToJapanese: 'Назад к японскому',
    radicals: 'Ключи: {radicals}',
    noContent: 'Содержимого пока нет.',
    noContentAdmin: 'Содержимого пока нет. Нажмите «Создать содержимое», чтобы создать его.',
    linksFrom: 'Связи от этого узла',
    linksTo: 'Связи с этим узлом',
    outgoing: {
      contains: 'Содержит',
      composed_of: 'Состоит из',
      uses_rule: 'Использует правило',
      example_of: 'Пример',
      exception_to: 'Исключение из',
      synonym_of: 'Синоним',
      related_to: 'Связано',
      same_kanji_as: 'Тот же кандзи, что и',
    },
    incoming: {
      contains: 'Встречается в',
      composed_of: 'Используется в словах',
      uses_rule: 'Предложения с этим правилом',
      example_of: 'Примеры',
      exception_to: 'Исключения',
      synonym_of: 'Синонимы',
      related_to: 'Связано',
      same_kanji_as: 'Тот же кандзи, что и',
    },

    editTitle: 'Изменить заголовок',
    generateContent: 'Создать содержимое',
    approve: 'Одобрить',
    regenerate: 'Создать заново',
    generateDialog: {
      text: 'Необязательные заметки для модели (например, «используй форму в кандзи 中», «считай это существительным, а не глаголом», «это вежливая связка»). Оставьте пустым, чтобы создать по стандартным правилам.',
      label: 'Заметки (необязательно)',
      confirm: 'Создать',
    },
    editTitleDialog: {
      text: 'Измените основной текст этого узла. Для слов и предложений можно указать фуригану, например 漢字(かんじ).',
      label: 'Заголовок',
      confirm: 'Сохранить',
    },
    error: 'Ошибка',
    generateFailed: 'Не удалось создать содержимое: {error}',
    updateTitleFailed: 'Не удалось изменить заголовок: {error}',
    approveFailed: 'Не удалось одобрить: {error}',
  },
};
