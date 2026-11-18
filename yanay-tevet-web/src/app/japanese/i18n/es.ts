import {JapaneseStrings} from './en';

export const es: JapaneseStrings = {
  title: 'Japonés',
  subtitle: 'Explora una red de textos, oraciones, palabras, kanji, partículas y reglas gramaticales.',
  nav: {
    explore: 'Explorar',
    ingest: 'Importar',
    review: 'Revisar',
  },
  tabs: {
    passage: 'Textos',
    sentence: 'Oraciones',
    word: 'Palabras',
    kanji: 'Kanji',
    particle: 'Partículas',
    rule: 'Reglas',
  },
  nodeTypes: {
    passage: 'Texto',
    sentence: 'Oración',
    word: 'Palabra',
    kanji: 'Kanji',
    particle: 'Partícula',
    rule: 'Regla',
  },
  statuses: {
    stub: 'Borrador',
    generating: 'Generando',
    needs_review: 'Pendiente de revisión',
    published: 'Publicado',
  },

  explore: {
    shuffle: 'Mezclar',
    loadFailed: 'No se pudo cargar. Vuelve a intentarlo en un momento.',
    emptyText: 'Aquí aparecen los textos importados y los elementos generados a partir de ellos.',
    emptyTitles: {
      passage: 'Aún no hay textos',
      sentence: 'Aún no hay oraciones',
      word: 'Aún no hay palabras',
      kanji: 'Aún no hay kanji',
      particle: 'Aún no hay partículas',
      rule: 'Aún no hay reglas',
    },
  },

  speak: {
    readAloud: 'Leer en voz alta en japonés',
    stop: 'Detener',
    loop: 'Repetir',
    loopOn: 'Repetición activada',
  },

  detail: {
    loading: 'Cargando',
    notFound: 'No se encontró el nodo.',
    backToJapanese: 'Volver a Japonés',
    radicals: 'Radicales: {radicals}',
    noContent: 'Aún no hay contenido.',
    noContentAdmin: 'Aún no hay contenido. Haz clic en «Generar contenido» para crearlo.',
    linksFrom: 'Enlaces desde este nodo',
    linksTo: 'Enlaces a este nodo',
    outgoing: {
      contains: 'Contiene',
      composed_of: 'Compuesto de',
      uses_rule: 'Usa la regla',
      example_of: 'Ejemplo de',
      exception_to: 'Excepción a',
      synonym_of: 'Sinónimo de',
      related_to: 'Relacionado',
      same_kanji_as: 'Mismo kanji que',
    },
    incoming: {
      contains: 'Aparece en',
      composed_of: 'Se usa en palabras',
      uses_rule: 'Oraciones que usan esta regla',
      example_of: 'Ejemplos',
      exception_to: 'Excepciones',
      synonym_of: 'Sinónimos',
      related_to: 'Relacionado',
      same_kanji_as: 'Mismo kanji que',
    },

    editTitle: 'Editar título',
    generateContent: 'Generar contenido',
    approve: 'Aprobar',
    regenerate: 'Regenerar',
    generateDialog: {
      text: 'Notas opcionales para guiar al modelo (p. ej., «usa la forma en kanji 中», «trátalo como sustantivo, no como verbo», «es la cópula cortés»). Déjalo vacío para generar con las reglas predeterminadas.',
      label: 'Notas (opcional)',
      confirm: 'Generar',
    },
    editTitleDialog: {
      text: 'Actualiza el texto principal que se muestra para este nodo. En palabras y oraciones puedes incluir furigana como 漢字(かんじ).',
      label: 'Título',
      confirm: 'Guardar',
    },
    error: 'Error',
    generateFailed: 'No se pudo generar el contenido: {error}',
    updateTitleFailed: 'No se pudo actualizar el título: {error}',
    approveFailed: 'No se pudo aprobar: {error}',
  },
};
