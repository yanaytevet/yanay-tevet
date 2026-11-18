// A translated sentence split around its `{name}` placeholders, so a template can style the filled-in
// values (a genre name in bold) without building the sentence from fragments.
export interface TextPart {
  text: string;
  isValue: boolean;
}

export function fillParts(template: string, values: Record<string, string | number>): TextPart[] {
  return template
    .split(/(\{\w+\})/)
    .filter(piece => piece !== '')
    .map(piece => {
      const key = /^\{(\w+)\}$/.exec(piece)?.[1];
      return key !== undefined && key in values
        ? {text: String(values[key]), isValue: true}
        : {text: piece, isValue: false};
    });
}
