import {JapaneseStrings} from './en';

export const fr: JapaneseStrings = {
  title: 'Japonais',
  subtitle: 'Explorez un réseau de textes, de phrases, de mots, de kanji, de particules et de règles de grammaire.',
  nav: {
    explore: 'Explorer',
    ingest: 'Importer',
    review: 'Relire',
  },
  tabs: {
    passage: 'Textes',
    sentence: 'Phrases',
    word: 'Mots',
    kanji: 'Kanji',
    particle: 'Particules',
    rule: 'Règles',
  },
  nodeTypes: {
    passage: 'Texte',
    sentence: 'Phrase',
    word: 'Mot',
    kanji: 'Kanji',
    particle: 'Particule',
    rule: 'Règle',
  },
  statuses: {
    stub: 'Ébauche',
    generating: 'En cours de génération',
    needs_review: 'À relire',
    published: 'Publié',
  },

  explore: {
    shuffle: 'Mélanger',
    loadFailed: 'Échec du chargement. Réessayez dans un instant.',
    emptyText: 'Les textes importés et les éléments générés à partir d’eux apparaissent ici.',
    emptyTitles: {
      passage: 'Aucun texte pour l’instant',
      sentence: 'Aucune phrase pour l’instant',
      word: 'Aucun mot pour l’instant',
      kanji: 'Aucun kanji pour l’instant',
      particle: 'Aucune particule pour l’instant',
      rule: 'Aucune règle pour l’instant',
    },
  },

  speak: {
    readAloud: 'Lire à voix haute en japonais',
    stop: 'Arrêter',
    loop: 'En boucle',
    loopOn: 'Lecture en boucle activée',
  },

  detail: {
    loading: 'Chargement',
    notFound: 'Nœud introuvable.',
    backToJapanese: 'Retour au japonais',
    radicals: 'Radicaux : {radicals}',
    noContent: 'Pas encore de contenu.',
    noContentAdmin: 'Pas encore de contenu. Cliquez sur « Générer le contenu » pour le créer.',
    linksFrom: 'Liens depuis ce nœud',
    linksTo: 'Liens vers ce nœud',
    outgoing: {
      contains: 'Contient',
      composed_of: 'Composé de',
      uses_rule: 'Utilise la règle',
      example_of: 'Exemple de',
      exception_to: 'Exception à',
      synonym_of: 'Synonyme de',
      related_to: 'Lié',
      same_kanji_as: 'Même kanji que',
    },
    incoming: {
      contains: 'Apparaît dans',
      composed_of: 'Utilisé dans les mots',
      uses_rule: 'Phrases utilisant cette règle',
      example_of: 'Exemples',
      exception_to: 'Exceptions',
      synonym_of: 'Synonymes',
      related_to: 'Lié',
      same_kanji_as: 'Même kanji que',
    },

    editTitle: 'Modifier le titre',
    generateContent: 'Générer le contenu',
    approve: 'Approuver',
    regenerate: 'Régénérer',
    generateDialog: {
      text: 'Notes facultatives pour guider le modèle (par ex. « utilise la forme kanji 中 », « traite-le comme un nom, pas un verbe », « c’est la copule polie »). Laissez vide pour générer avec les règles par défaut.',
      label: 'Notes (facultatif)',
      confirm: 'Générer',
    },
    editTitleDialog: {
      text: 'Modifiez le texte principal affiché pour ce nœud. Pour les mots et les phrases, vous pouvez ajouter des furigana comme 漢字(かんじ).',
      label: 'Titre',
      confirm: 'Enregistrer',
    },
    error: 'Erreur',
    generateFailed: 'Impossible de générer le contenu : {error}',
    updateTitleFailed: 'Impossible de modifier le titre : {error}',
    approveFailed: 'Impossible d’approuver : {error}',
  },
};
