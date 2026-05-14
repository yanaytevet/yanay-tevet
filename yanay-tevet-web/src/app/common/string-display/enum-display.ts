import {Option} from '../interfaces/util/option';

export class EnumDisplay {
  data: Record<string, string> = {};
  options: Option[] = [];

  constructor() {
    this.options = this.getOptions();
  }

  public get(key: any): string {
    if (key in this.data) {
      return this.data[key];
    }
    return key;
  }

  public getKeys(): string[] {
    return Object.keys(this.data);
  }

  public getOptions(): Option[] {
    return this.getKeys().map(key => {
      return {display: this.get(key), value: key};
    });
  }
}
