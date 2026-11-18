import {JapaneseStrings} from './en';

export const de: JapaneseStrings = {
  title: 'Japanisch',
  subtitle: 'Entdecke ein Netz aus Texten, Sätzen, Wörtern, Kanji, Partikeln und Grammatikregeln.',
  nav: {
    explore: 'Entdecken',
    ingest: 'Import',
    review: 'Prüfen',
  },
  tabs: {
    passage: 'Texte',
    sentence: 'Sätze',
    word: 'Wörter',
    kanji: 'Kanji',
    particle: 'Partikeln',
    rule: 'Regeln',
  },
  nodeTypes: {
    passage: 'Text',
    sentence: 'Satz',
    word: 'Wort',
    kanji: 'Kanji',
    particle: 'Partikel',
    rule: 'Regel',
  },
  statuses: {
    stub: 'Entwurf',
    generating: 'Wird erstellt',
    needs_review: 'Zu prüfen',
    published: 'Veröffentlicht',
  },

  explore: {
    shuffle: 'Mischen',
    loadFailed: 'Laden fehlgeschlagen. Versuch es gleich noch einmal.',
    emptyText: 'Importierte Texte und die daraus erzeugten Einträge erscheinen hier.',
    emptyTitles: {
      passage: 'Noch keine Texte',
      sentence: 'Noch keine Sätze',
      word: 'Noch keine Wörter',
      kanji: 'Noch keine Kanji',
      particle: 'Noch keine Partikeln',
      rule: 'Noch keine Regeln',
    },
  },

  speak: {
    readAloud: 'Auf Japanisch vorlesen',
    stop: 'Stopp',
    loop: 'Wiederholen',
    loopOn: 'Wiederholung an',
  },

  detail: {
    loading: 'Wird geladen',
    notFound: 'Knoten nicht gefunden.',
    backToJapanese: 'Zurück zu Japanisch',
    radicals: 'Radikale: {radicals}',
    noContent: 'Noch kein Inhalt.',
    noContentAdmin: 'Noch kein Inhalt. Klicke auf „Inhalt erzeugen“, um ihn zu erstellen.',
    linksFrom: 'Verweise von diesem Knoten',
    linksTo: 'Verweise auf diesen Knoten',
    outgoing: {
      contains: 'Enthält',
      composed_of: 'Besteht aus',
      uses_rule: 'Verwendet Regel',
      example_of: 'Beispiel für',
      exception_to: 'Ausnahme zu',
      synonym_of: 'Synonym von',
      related_to: 'Verwandt',
      same_kanji_as: 'Gleiches Kanji wie',
    },
    incoming: {
      contains: 'Kommt vor in',
      composed_of: 'Verwendet in Wörtern',
      uses_rule: 'Sätze mit dieser Regel',
      example_of: 'Beispiele',
      exception_to: 'Ausnahmen',
      synonym_of: 'Synonyme',
      related_to: 'Verwandt',
      same_kanji_as: 'Gleiches Kanji wie',
    },

    editTitle: 'Titel bearbeiten',
    generateContent: 'Inhalt erzeugen',
    approve: 'Freigeben',
    regenerate: 'Neu erzeugen',
    generateDialog: {
      text: 'Optionale Hinweise für das Modell (z. B. „verwende die Kanji-Form 中“, „behandle das als Nomen, nicht als Verb“, „das ist die höfliche Kopula“). Leer lassen, um mit den Standardregeln zu erzeugen.',
      label: 'Hinweise (optional)',
      confirm: 'Erzeugen',
    },
    editTitleDialog: {
      text: 'Ändere den Haupttext dieses Knotens. Bei Wörtern und Sätzen kannst du Furigana wie 漢字(かんじ) angeben.',
      label: 'Titel',
      confirm: 'Speichern',
    },
    error: 'Fehler',
    generateFailed: 'Inhalt konnte nicht erzeugt werden: {error}',
    updateTitleFailed: 'Titel konnte nicht geändert werden: {error}',
    approveFailed: 'Freigabe fehlgeschlagen: {error}',
  },
};
